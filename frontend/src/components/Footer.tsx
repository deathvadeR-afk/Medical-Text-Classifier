import React from 'react';
import './Footer.css';

const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <p>&copy; 2024 Medical Text Classifier. Built with React & FastAPI.</p>
          <div className="footer-links">
            <a href="#" className="footer-link">
              <i className="fab fa-github"></i>
              GitHub
            </a>
            <a href="#" className="footer-link">
              <i className="fas fa-book"></i>
              Documentation
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
