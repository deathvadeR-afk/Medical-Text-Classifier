import React, { useState } from 'react';
import axios from 'axios';
import './ClassificationForm.css';
import ResultDisplay from './ResultDisplay';
import LoadingSpinner from './LoadingSpinner';

interface PredictionResult {
  predicted_class: string;
  confidence: number;
  probabilities: Record<string, number>;
}

const ClassificationForm: React.FC = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exampleTexts = [
    "What are the symptoms of diabetes?",
    "I have chest pain and shortness of breath",
    "What are the treatment options for breast cancer?",
    "My grandmother has Alzheimer's disease",
    "What causes high blood pressure?",
    "How is lung cancer diagnosed?"
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setError('Please enter some medical text to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('/predict', {
        text: text.trim()
      });
      
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred while processing your request');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleText: string) => {
    setText(exampleText);
    setResult(null);
    setError(null);
  };

  const handleClear = () => {
    setText('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="classification-form fade-in">
      <div className="form-card">
        <div className="form-header">
          <h2>
            <i className="fas fa-microscope"></i>
            Analyze Medical Text
          </h2>
          <p>Enter medical symptoms, questions, or descriptions to get AI-powered disease category predictions</p>
        </div>

        <form onSubmit={handleSubmit} className="form">
          <div className="input-group">
            <label htmlFor="medical-text" className="label">
              Medical Text
            </label>
            <textarea
              id="medical-text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter medical symptoms, questions, or descriptions here..."
              className="textarea"
              rows={4}
              maxLength={1000}
            />
            <div className="char-count">
              {text.length}/1000 characters
            </div>
          </div>

          <div className="button-group">
            <button
              type="submit"
              disabled={loading || !text.trim()}
              className="btn btn-primary"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="small" />
                  Analyzing...
                </>
              ) : (
                <>
                  <i className="fas fa-search"></i>
                  Analyze Text
                </>
              )}
            </button>
            
            <button
              type="button"
              onClick={handleClear}
              className="btn btn-secondary"
              disabled={loading}
            >
              <i className="fas fa-eraser"></i>
              Clear
            </button>
          </div>
        </form>

        <div className="examples-section">
          <h3>Try these examples:</h3>
          <div className="examples-grid">
            {exampleTexts.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="example-btn"
                disabled={loading}
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="error-message">
            <i className="fas fa-exclamation-triangle"></i>
            {error}
          </div>
        )}

        {loading && (
          <div className="loading-section">
            <LoadingSpinner size="large" />
            <p>Analyzing your medical text...</p>
          </div>
        )}

        {result && !loading && (
          <ResultDisplay result={result} />
        )}
      </div>
    </div>
  );
};

export default ClassificationForm;
