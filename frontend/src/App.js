import React from 'react';
import { Routes, Route, Navigate } from 'react-router';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import Feed from './components/Feed';
import LoginPage from './pages/LoginPage';
import MainPage from './pages/MainPage';
import RegisterPage from './pages/RegisterPage';
import PostPage from './pages/PostPage';
import ProfilePage from './pages/ProfilePage';
import EditProfilePage from './pages/EditProfilePage';

function App() {
  return (<>
    <AuthProvider>
      <Navbar />
      <div className="container">
        <div className="row justify-content-center py-2">
          <div className="col-6">
            <Routes>
              <Route path="/" element={<MainPage />}>
                <Route index element={<Navigate to="/recommended" replace />} />
                <Route path="recommended" element={<Feed />} />
                <Route path="followed" element={<Feed followed />} />
              </Route>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/post/:postId" element={<PostPage />} />
              <Route path="/@/:username" element={<ProfilePage />} />
              <Route path="/edit-profile" element={<EditProfilePage />} />
            </Routes>                 
          </div>
        </div>
      </div>
    </AuthProvider>
  </>);
}

export default App;