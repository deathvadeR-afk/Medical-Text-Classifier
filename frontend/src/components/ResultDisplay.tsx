import React from 'react';
import './ResultDisplay.css';

interface PredictionResult {
  predicted_class: string;
  confidence: number;
  probabilities: Record<string, number>;
}

interface ResultDisplayProps {
  result: PredictionResult;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ result }) => {
  const { predicted_class, confidence, probabilities } = result;

  // Get category icon and color
  const getCategoryInfo = (category: string) => {
    switch (category) {
      case 'Cancers':
        return { icon: 'fas fa-ribbon', color: '#e74c3c', bgColor: '#fdf2f2' };
      case 'Cardiovascular Diseases':
        return { icon: 'fas fa-heartbeat', color: '#e91e63', bgColor: '#fdf2f8' };
      case 'Metabolic & Endocrine Disorders':
        return { icon: 'fas fa-dna', color: '#9c27b0', bgColor: '#f3e5f5' };
      case 'Neurological & Cognitive Disorders':
        return { icon: 'fas fa-brain', color: '#3f51b5', bgColor: '#e8eaf6' };
      case 'Other Age-Related & Immune Disorders':
        return { icon: 'fas fa-shield-alt', color: '#607d8b', bgColor: '#eceff1' };
      default:
        return { icon: 'fas fa-question-circle', color: '#666', bgColor: '#f5f5f5' };
    }
  };

  const categoryInfo = getCategoryInfo(predicted_class);
  const confidencePercentage = Math.round(confidence * 100);

  // Sort probabilities by value
  const sortedProbabilities = Object.entries(probabilities)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5); // Show top 5

  const getConfidenceLevel = (conf: number) => {
    if (conf >= 0.8) return { level: 'High', color: '#4caf50' };
    if (conf >= 0.6) return { level: 'Medium', color: '#ff9800' };
    return { level: 'Low', color: '#f44336' };
  };

  const confidenceLevel = getConfidenceLevel(confidence);

  return (
    <div className="result-display fade-in">
      <div className="result-header">
        <h3>
          <i className="fas fa-chart-line"></i>
          Analysis Results
        </h3>
      </div>

      <div className="main-prediction">
        <div className="prediction-card" style={{ backgroundColor: categoryInfo.bgColor }}>
          <div className="prediction-icon" style={{ color: categoryInfo.color }}>
            <i className={categoryInfo.icon}></i>
          </div>
          <div className="prediction-content">
            <h4>Predicted Category</h4>
            <p className="category-name">{predicted_class}</p>
            <div className="confidence-info">
              <span className="confidence-label">Confidence:</span>
              <span 
                className="confidence-value" 
                style={{ color: confidenceLevel.color }}
              >
                {confidencePercentage}% ({confidenceLevel.level})
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="confidence-bar-container">
        <div className="confidence-label-bar">Confidence Level</div>
        <div className="confidence-bar">
          <div 
            className="confidence-fill" 
            style={{ 
              width: `${confidencePercentage}%`,
              backgroundColor: confidenceLevel.color 
            }}
          ></div>
        </div>
        <div className="confidence-percentage">{confidencePercentage}%</div>
      </div>

      <div className="all-probabilities">
        <h4>
          <i className="fas fa-chart-bar"></i>
          All Category Probabilities
        </h4>
        <div className="probability-list">
          {sortedProbabilities.map(([category, probability], index) => {
            const categoryInfo = getCategoryInfo(category);
            const percentage = Math.round(probability * 100);
            
            return (
              <div key={category} className="probability-item">
                <div className="probability-header">
                  <div className="category-info">
                    <i 
                      className={categoryInfo.icon} 
                      style={{ color: categoryInfo.color }}
                    ></i>
                    <span className="category-name">{category}</span>
                  </div>
                  <span className="percentage">{percentage}%</span>
                </div>
                <div className="probability-bar">
                  <div 
                    className="probability-fill"
                    style={{ 
                      width: `${percentage}%`,
                      backgroundColor: categoryInfo.color,
                      opacity: index === 0 ? 1 : 0.7
                    }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="disclaimer">
        <i className="fas fa-info-circle"></i>
        <p>
          <strong>Disclaimer:</strong> This is an AI-powered analysis tool for educational purposes. 
          Always consult with qualified healthcare professionals for medical advice and diagnosis.
        </p>
      </div>
    </div>
  );
};

export default ResultDisplay;
