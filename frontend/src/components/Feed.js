import React, { useState, useEffect, useRef } from 'react';
import CreatePostForm from '../components/CreatePostForm';
import Post from './Post';
import { useAuth } from '../contexts/AuthContext';
import { getPosts } from '../services/posts';


function Feed({ parent=null }) {
  const feedRef = useRef(null);

  const { user } = useAuth();

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [next, setNext] = useState(null);

  const addToFeed = post => {
    setPosts(prev => [post, ...prev]);
  };

  const deleteFromFeed = id => {
    setPosts(prev => prev.filter(post => post.id !== id));
  };

  const likeInFeed = id => {
    setPosts(prev => prev.map(post => post.id === id ? {
      ...post,
      liked_by: [...post.liked_by, user.id],
      likes_count: post.likes_count + 1
    } : post))
  }

  const unlikeInFeed = id => {
    setPosts(prev => prev.map(post => post.id === id ? {
      ...post,
      liked_by: post.liked_by.filter(like => like !== user.id),
      likes_count: post.likes_count - 1
    } : post))
  }

  const loadPosts = async (cursor=null) => {
    if (loading || (!cursor && posts.length > 0)) return;
    
    setLoading(true);

    try {
      const data = await getPosts(parent, cursor);

      setPosts(prev => cursor ? [...prev, ...data.results] : data.results);
      setNext(data.next);
    }
    catch (error) {
      setError(error.message);
    }
    finally {
      setLoading(false);    
    }
  }

  useEffect(() => {
    loadPosts();
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight;
      const clientHeight = window.innerHeight;

      if (scrollTop + clientHeight >= scrollHeight -1 && !loading && next) {
        const cursor = next ? new URLSearchParams(next.split('?')[1]).get('cursor') : null;
        loadPosts(cursor);
      }
    };

    window.addEventListener('scroll', handleScroll);

    return () => window.removeEventListener('scroll', handleScroll);
  }, [loading, next]);

  return (<>
    <CreatePostForm parent={parent} addToFeed={addToFeed} />

    {posts && posts.map(post => (
      <Post
        key={post.id}
        post={post}
        like={likeInFeed}
        unlike={unlikeInFeed}
        remove={deleteFromFeed}
        isReply={parent ? true : false}
      />
    ))}

    {loading && (<>
      <div className="text-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>      
      </div>
    </>)}
  </>);
}

export default Feed;