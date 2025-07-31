import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getPosts } from '../services/posts';
import LoginForm from '../components/LoginForm';
import { Link } from 'react-router';
import Feed from '../components/Feed';

function MainPage() {
  const { user } = useAuth();

  return user ? (<>
    <Feed />

  </>) : (<>
    <LoginForm />
    Nie masz konta? <Link to="/register">Zarejestruj się</Link>
  </>);
}

export default MainPage;