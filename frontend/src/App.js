import React from 'react';
import { Routes, Route } from 'react-router';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import MainPage from './pages/MainPage';
import RegisterPage from './pages/RegisterPage';

function App() {
  return (<>
    <AuthProvider>
      <Navbar />
      <div className="container">
        <div className="row">
          <div className="col-12">
            <Routes>
              <Route path="/" element={<MainPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Routes>                 
          </div>
        </div>
      </div>
    </AuthProvider>
  </>);
}

export default App;