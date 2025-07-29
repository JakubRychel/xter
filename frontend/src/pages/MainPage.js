import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getPosts } from '../services/posts';
import LoginForm from '../components/LoginForm';
import { Link } from 'react-router';
import Feed from '../components/Feed';

function MainPage() {
  const { user } = useAuth();

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const data = await getPosts();
        setPosts(data);
      }
      catch (error) {
        setError(error.message);
      }
      finally {
        setLoading(false);
      }
    }

    fetchPosts();
  }, []);

  if (loading) return (<>
    <div className="text-center">
      <div className="spinner-border" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>      
    </div>
  </>);

  return user ? (<>
    <Feed data={posts} />

  </>) : (<>
    <LoginForm />
    Nie masz konta? <Link to="/register">Zarejestruj się</Link>
  </>);
}

export default MainPage;