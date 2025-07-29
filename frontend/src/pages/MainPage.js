import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoginForm from '../components/LoginForm';
import { Link } from 'react-router';
import CreatePostForm from '../components/CreatePostForm';
import Feed from '../components/Feed';

function MainPage() {
  const { user } = useAuth();

  return user ? (<>
    <CreatePostForm />
    <Feed />

  </>) : (<>
    <LoginForm />
    Nie masz konta? <Link to="register/">Zarejestruj się</Link>
  </>);
}

export default MainPage;