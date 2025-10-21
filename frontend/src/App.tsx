import React from 'react';
import './App.css';
import Header from './components/Header';
import ClassificationForm from './components/ClassificationForm';
import Footer from './components/Footer';

function App() {
  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <div className="container">
          <ClassificationForm />
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default App;
