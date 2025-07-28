import React from 'react';
import { createRoot } from 'react-dom/client';
//import bootstrap from 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import App from './App';


const rootElement = document.getElementById('app');
const root = createRoot(rootElement);
root.render(
  <React.StrictMode>
      <App />
  </React.StrictMode>
);