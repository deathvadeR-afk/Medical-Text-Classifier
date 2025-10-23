import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.inference import MedicalTextClassifier

def test_inference():
    classifier = MedicalTextClassifier()
    
    # Test that the model loading fails gracefully
    try:
        classifier.load_model()
        print("Model loading completed (unexpected)")
    except Exception as e:
        print(f"Model loading failed as expected: {e}")
    
    # Test that the classifier is not loaded
    print(f"Classifier loaded: {classifier.is_loaded()}")
    
    # Test rule-based classification
    test_texts = [
        "What are the symptoms of breast cancer?",
        "I have high blood pressure and chest pain",
        "My blood sugar levels are too high",
        "I'm experiencing memory loss and confusion",
        "I have a common cold"
    ]
    
    for text in test_texts:
        try:
            predicted_class, confidence, probabilities = classifier.predict(text)
            print(f"Text: {text}")
            print(f"Predicted class: {predicted_class}")
            print(f"Confidence: {confidence}")
            print(f"Probabilities: {probabilities}")
            print("---")
        except Exception as e:
            print(f"Error predicting for '{text}': {e}")

if __name__ == "__main__":
    test_inference()