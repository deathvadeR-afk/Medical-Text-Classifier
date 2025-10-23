# 🚀 Simple Render Deployment Guide
## Medical Text Classification App

**Quick and easy steps to deploy your app to Render.com**

---

## 📋 **Prerequisites**

1. ✅ **Render Account**: Sign up at [render.com](https://render.com) (free)
2. ✅ **GitHub Account**: Your code is already on GitHub
3. ✅ **Model Files**: You have model files in the `models/` directory
4. ✅ **Working App**: Your app runs locally (which it does!)

---

## 🎯 **Step-by-Step Deployment**

### **Step 1: Create Render Account**
1. Go to [render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with GitHub (recommended)
4. Connect your GitHub account

### **Step 2: Deploy Using Blueprint (Easiest Method)**
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your repository: `Medical-Text-Classification`
4. Render will automatically detect your `render.yaml` file
5. Click **"Apply"**

**That's it!** Render will automatically create:
- PostgreSQL database (`medtext-db`)
- API backend service (`medtext-api`)
- Frontend static site (`medtext-frontend`)

### **Step 3: Configure Environment Variables**
After blueprint deployment, you need to set a few secure values:

1. Go to your **API service** (`medtext-api`)
2. Click **"Environment"** tab
3. Update these variables:

```bash
# Generate a secure secret key (run this locally):
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate API keys (run this locally):
python -c "import secrets; print(','.join([secrets.token_urlsafe(32) for _ in range(3)]))"
```

4. Set these in Render:
   - `SECRET_KEY`: Use the generated secret key
   - `API_KEYS`: Use the generated API keys

### **Step 4: Wait for Deployment**
- **Database**: ~2-3 minutes
- **API Backend**: ~5-10 minutes (Docker build)
- **Frontend**: ~3-5 minutes

### **Step 5: Test Your Deployment**
1. **Health Check**: Visit `https://medtext-api.onrender.com/health`
2. **Frontend**: Visit `https://medtext-frontend.onrender.com`
3. **API Docs**: Visit `https://medtext-api.onrender.com/docs`

---

## 🔧 **Alternative: Manual Deployment**

If blueprint doesn't work, deploy manually:

### **A. Create Database**
1. **New +** → **PostgreSQL**
2. **Name**: `medtext-db`
3. **Database**: `medtext_prod`
4. **Plan**: Starter ($7/month)
5. **Create Database**

### **B. Create API Service**
1. **New +** → **Web Service**
2. **Repository**: Select your repo
3. **Name**: `medtext-api`
4. **Environment**: Docker
5. **Plan**: Standard ($25/month)
6. **Environment Variables**:
   ```
   ENVIRONMENT=production
   DEBUG=false
   LOG_LEVEL=INFO
   SECRET_KEY=your-generated-secret-key
   API_KEYS=your-generated-api-keys
   REQUIRE_API_KEY=true
   ALLOWED_ORIGINS=https://medtext-frontend.onrender.com
   ALLOWED_HOSTS=medtext-api.onrender.com
   ```
7. **Connect Database**: Add `medtext-db` in Environment section
8. **Create Web Service**

### **C. Create Frontend Service**
1. **New +** → **Static Site**
2. **Repository**: Same repo
3. **Name**: `medtext-frontend`
4. **Root Directory**: `frontend`
5. **Build Command**: `npm ci && npm run build`
6. **Publish Directory**: `build`
7. **Environment Variables**:
   ```
   NODE_ENV=production
   REACT_APP_API_URL=https://medtext-api.onrender.com
   REACT_APP_ENVIRONMENT=production
   ```
8. **Create Static Site**

---

## ✅ **Verification Checklist**

After deployment, check these:

- [ ] **API Health**: `https://medtext-api.onrender.com/health` returns 200
- [ ] **Frontend Loads**: `https://medtext-frontend.onrender.com` shows the app
- [ ] **API Docs**: `https://medtext-api.onrender.com/docs` shows Swagger UI
- [ ] **Prediction Works**: Test a prediction through the frontend
- [ ] **No Errors**: Check logs in Render dashboard

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: Build Fails**
- **Solution**: Check that all model files are committed to GitHub
- **Check**: Logs in Render dashboard for specific errors

### **Issue 2: Model Not Loading**
- **Solution**: Verify `models/` directory has all required files:
  - `label_mapping.json`
  - `reverse_label_mapping.json`
  - Model checkpoint files

### **Issue 3: CORS Errors**
- **Solution**: Update `ALLOWED_ORIGINS` with correct frontend URL
- **Format**: `https://medtext-frontend.onrender.com` (no trailing slash)

### **Issue 4: Database Connection**
- **Solution**: Ensure database is connected in API service environment variables
- **Check**: `DATABASE_URL` should be auto-populated

---

## 💰 **Cost Breakdown**

- **PostgreSQL Starter**: $7/month
- **API Standard Plan**: $25/month  
- **Frontend Static Site**: FREE
- **Total**: ~$32/month

**Start with Starter plans and upgrade if needed!**

---

## 🎉 **Success!**

Once deployed, your app will be available at:
- **Frontend**: `https://medtext-frontend.onrender.com`
- **API**: `https://medtext-api.onrender.com`
- **Docs**: `https://medtext-api.onrender.com/docs`

**Your Medical Text Classification app is now live on the internet!** 🌐
