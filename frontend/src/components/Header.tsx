import React from 'react';
import './Header.css';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="logo">
            <i className="fas fa-stethoscope"></i>
            <h1>Medical Text Classifier</h1>
          </div>
          <p className="subtitle">
            AI-powered medical symptom analysis and disease prediction
          </p>
        </div>
      </div>
    </header>
  );
};

export default Header;
