import React from 'react';
import { Routes, Route } from 'react-router';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import MainPage from './pages/MainPage';
import RegisterPage from './pages/RegisterPage';
import PostPage from './pages/PostPage';

function App() {
  return (<>
    <AuthProvider>
      <Navbar />
      <div className="container">
        <div className="row justify-content-center py-2">
          <div className="col-6">
            <Routes>
              <Route path="/" element={<MainPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/post/:postId" element={<PostPage />} />
            </Routes>                 
          </div>
        </div>
      </div>
    </AuthProvider>
  </>);
}

export default App;