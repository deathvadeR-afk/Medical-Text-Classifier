# 🏥 Google Colab Training Guide - BiomedBERT Model

## 📋 Overview

This guide explains how to train the BiomedBERT model on Google Colab (with free GPU) and integrate it into your production application, **eliminating the need for local training, DVC, and MLflow**.

---

## 🎯 Why Use Colab for Training?

### ✅ **Advantages:**
1. **Free GPU Access** - Train in 10-15 minutes instead of hours on CPU
2. **No Local Resources** - Don't strain your local machine
3. **Reproducible** - Same environment every time
4. **Simple Deployment** - Just download and use the trained model

### ❌ **What You Can Remove from Your Project:**
- ❌ **DVC (Data Version Control)** - Not needed since you're training externally
- ❌ **MLflow** - Not needed for training tracking (optional for production monitoring)
- ❌ **Grafana** - Not needed for MVP (optional for advanced monitoring)
- ❌ **Database Training Data Storage** - Train directly from CSV
- ❌ **`train_model.py`** - Training happens on Colab

### ✅ **What to Keep:**
- ✅ **FastAPI Backend** - For serving predictions
- ✅ **React Frontend** - User interface
- ✅ **Trained Model Files** - Downloaded from Colab
- ✅ **Docker** (optional) - For deployment
- ✅ **CI/CD Pipeline** - For automated deployment
- ⚠️ **PostgreSQL** (optional) - Only if you want to log predictions for analytics

---

## 🚀 Step-by-Step Training Process

### **Step 1: Prepare Your Dataset**

1. Ensure you have `data/medical_texts.csv` in your project
2. Verify it contains the required columns: `question`, `answer`, `source`, `focus_area`

### **Step 2: Open the Colab Notebook**

1. Navigate to `notebooks/Train_BiomedBERT_Colab.ipynb` in your project
2. Upload it to Google Colab:
   - Go to [Google Colab](https://colab.research.google.com/)
   - Click **File → Upload notebook**
   - Select `Train_BiomedBERT_Colab.ipynb`

### **Step 3: Enable GPU**

1. In Colab, click **Runtime → Change runtime type**
2. Select **GPU** (T4 or better)
3. Click **Save**

### **Step 4: Upload Dataset**

1. Run the "Upload Dataset" cell
2. Click the **Choose Files** button
3. Upload your `medical_texts.csv` file

### **Step 5: Run Training**

1. Click **Runtime → Run all** (or run cells sequentially)
2. Wait ~10-15 minutes for training to complete
3. Monitor the training progress and accuracy

**Expected Output:**
```
Epoch 1/10, Average CE Loss: 0.8234
Epoch 2/10, Average CE Loss: 0.3456
...
Epoch 10/10, Average CE Loss: 0.0116

🎯 Test Accuracy: 99.17%
```

### **Step 6: Download the Trained Model**

1. Run the final cell to download `biomedbert_model.zip`
2. Extract the ZIP file on your local machine
3. You'll get a folder structure like:
   ```
   biomedbert_model/
   ├── model.pt                      # PyTorch model weights
   ├── config.json                   # Tokenizer config
   ├── vocab.txt                     # Vocabulary
   ├── tokenizer_config.json         # Tokenizer settings
   ├── label_mapping.json            # Focus group → label
   └── reverse_label_mapping.json    # Label → focus group
   ```

### **Step 7: Integrate into Your Project**

1. Create a `models/` directory in your project root (if it doesn't exist)
2. Place the extracted `biomedbert_model/` folder inside:
   ```
   your-project/
   ├── models/
   │   └── biomedbert_model/
   │       ├── model.pt
   │       ├── config.json
   │       ├── vocab.txt
   │       └── ...
   ├── src/
   ├── frontend/
   └── ...
   ```

---

## 🔧 Integrating the Model into FastAPI

### **Option 1: Create a New Model Service File**

Create `src/model_service.py`:

```python
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
import json
from pathlib import Path

# Model architecture (must match training)
class BiomedBERTClassifier(nn.Module):
    def __init__(self, bert_model, num_classes=5):
        super(BiomedBERTClassifier, self).__init__()
        self.bert = bert_model
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        logits = self.classifier(pooled_output)
        return logits

# Load model on startup
MODEL_DIR = Path(__file__).parent.parent / 'models' / 'biomedbert_model'
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))

# Load model
checkpoint = torch.load(str(MODEL_DIR / 'model.pt'), map_location=device)
bert_base = AutoModel.from_pretrained(checkpoint['model_config']['model_name'])
model = BiomedBERTClassifier(bert_base, num_classes=5).to(device)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Load label mapping
with open(MODEL_DIR / 'reverse_label_mapping.json', 'r') as f:
    label_to_focus_group = json.load(f)

def predict_focus_group(text: str) -> dict:
    """
    Predict the medical focus group for a given text.
    
    Args:
        text: Medical text to classify
        
    Returns:
        dict with 'focus_group', 'confidence', and 'all_probabilities'
    """
    # Tokenize input
    inputs = tokenizer(
        text,
        padding=True,
        truncation=True,
        return_tensors="pt",
        max_length=512
    ).to(device)
    
    # Get prediction
    with torch.no_grad():
        outputs = model(inputs['input_ids'], inputs['attention_mask'])
        prediction = torch.argmax(outputs, dim=1).item()
        probabilities = torch.softmax(outputs, dim=1)[0].cpu().numpy()
    
    return {
        'focus_group': label_to_focus_group[str(prediction)],
        'confidence': float(probabilities[prediction]),
        'all_probabilities': {
            label_to_focus_group[str(i)]: float(prob) 
            for i, prob in enumerate(probabilities)
        }
    }
```

### **Option 2: Update Existing FastAPI Endpoints**

Update `src/main.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.model_service import predict_focus_group

app = FastAPI(title="Medical Text Classification API")

class PredictionRequest(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    focus_group: str
    confidence: float
    all_probabilities: dict

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Classify medical text into one of 5 focus groups.
    """
    try:
        result = predict_focus_group(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "BiomedBERT", "accuracy": "99%"}
```

---

## 🧪 Testing the Model

### **Test with cURL:**

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient presents with chest pain and shortness of breath"}'
```

**Expected Response:**
```json
{
  "focus_group": "Cardiovascular Diseases",
  "confidence": 0.987,
  "all_probabilities": {
    "Neurological & Cognitive Disorders": 0.002,
    "Cancers": 0.001,
    "Cardiovascular Diseases": 0.987,
    "Metabolic & Endocrine Disorders": 0.008,
    "Other Age-Related & Immune Disorders": 0.002
  }
}
```

### **Test with Python:**

```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={"text": "Patient has elevated blood sugar levels and frequent urination"}
)

print(response.json())
# Expected: {"focus_group": "Metabolic & Endocrine Disorders", ...}
```

---

## 📊 Architecture Comparison

### **Before (Complex Setup):**
```
┌─────────────────────────────────────────────────────────┐
│  Local Training (Slow)                                  │
│  ├── PostgreSQL (training data storage)                │
│  ├── DVC (data versioning)                             │
│  ├── MLflow (experiment tracking)                      │
│  ├── Grafana (monitoring)                              │
│  └── train_model.py (local training script)            │
└─────────────────────────────────────────────────────────┘
```

### **After (Simplified Setup):**
```
┌─────────────────────────────────────────────────────────┐
│  Google Colab (Fast GPU Training)                       │
│  └── Train_BiomedBERT_Colab.ipynb                      │
└─────────────────────────────────────────────────────────┘
                    ↓ Download Model
┌─────────────────────────────────────────────────────────┐
│  Production App (Lightweight)                           │
│  ├── FastAPI (predictions)                             │
│  ├── React Frontend (UI)                               │
│  ├── Trained Model (models/biomedbert_model/)          │
│  └── Optional: PostgreSQL (prediction logging only)    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Retraining Workflow

When you need to retrain the model (e.g., with new data):

1. **Update Dataset:** Add new records to `medical_texts.csv`
2. **Upload to Colab:** Upload the updated CSV to Colab
3. **Run Training:** Execute all cells in the notebook
4. **Download New Model:** Download the updated `biomedbert_model.zip`
5. **Replace Old Model:** Replace the old model folder with the new one
6. **Restart API:** Restart your FastAPI server to load the new model

**No need to:**
- ❌ Commit large model files to Git (use Git LFS or document download link)
- ❌ Version datasets with DVC
- ❌ Track experiments with MLflow

---

## 📦 Deployment Considerations

### **Model Size:**
- The trained model is ~400-500 MB
- **Option 1:** Use Git LFS if deploying via Git
- **Option 2:** Store on Google Drive/Dropbox and download during deployment
- **Option 3:** Build model into Docker image (increases image size)

### **Recommended Deployment Approach:**

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY frontend/build/ ./frontend/build/

# Download model from external source (or copy if using Git LFS)
# Option 1: Copy from build context
COPY models/biomedbert_model/ ./models/biomedbert_model/

# Option 2: Download from URL during build
# RUN wget https://your-storage.com/biomedbert_model.zip && \
#     unzip biomedbert_model.zip -d models/ && \
#     rm biomedbert_model.zip

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ❓ FAQ

### **Q: Do I need to keep the database?**
**A:** Only if you want to log predictions for analytics. For a stateless prediction API, you can remove PostgreSQL entirely.

### **Q: Can I use the free Colab tier?**
**A:** Yes! The free tier provides T4 GPU which is sufficient. Training takes ~10-15 minutes.

### **Q: What if Colab disconnects during training?**
**A:** Colab free tier has session limits. If disconnected, you'll need to restart. Consider Colab Pro ($10/month) for longer sessions.

### **Q: How do I version my models?**
**A:** Simple approach: Name your model folders with versions (e.g., `biomedbert_model_v1`, `biomedbert_model_v2`). Document the version in your README or a `MODELS.md` file.

### **Q: Can I deploy this to production?**
**A:** Absolutely! The model is production-ready. Deploy your FastAPI app with the model to any cloud provider (AWS, GCP, Azure, Heroku, etc.).

---

## 🎉 Summary

**You've successfully:**
1. ✅ Trained BiomedBERT on Google Colab with GPU (~99% accuracy)
2. ✅ Downloaded the trained model
3. ✅ Integrated it into your FastAPI application
4. ✅ Simplified your architecture (removed DVC, MLflow, Grafana)
5. ✅ Created a lightweight, production-ready prediction API

**Next Steps:**
- Test the API with your frontend
- Deploy to production
- Monitor prediction performance
- Retrain when you have new data

---

**Need Help?** Check the example code in the Colab notebook or refer to the FastAPI integration examples above.

