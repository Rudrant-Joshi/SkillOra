import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';
import './styles/globals.css';

// Prevent selection & copying of static page text while allowing inputs/editors to function
document.addEventListener('selectstart', (e) => {
  const tag = e.target?.tagName?.toLowerCase();
  const isEditable = tag === 'input' || tag === 'textarea' || e.target?.isContentEditable || e.target?.closest?.('.monaco-editor');
  if (!isEditable) {
    e.preventDefault();
  }
});

document.addEventListener('copy', (e) => {
  const tag = e.target?.tagName?.toLowerCase();
  const isEditable = tag === 'input' || tag === 'textarea' || e.target?.isContentEditable || e.target?.closest?.('.monaco-editor');
  if (!isEditable) {
    e.preventDefault();
  }
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
