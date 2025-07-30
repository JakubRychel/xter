import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getPost } from '../services/posts';
import { useNavigate, useParams } from 'react-router';
import Post from '../components/Post';

function PostPage() {
  const { user } = useAuth();
  const { postId } = useParams();

  const [post, setPost] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const like = () => {
    setPost(prev => ({
      ...prev,
      likes: [...prev.likes, user.id],
      likes_count: prev.likes_count + 1
    }))
  }

  const unlike = () => {
    setPost(prev => ({
      ...prev,
      likes: prev.likes.filter(like => like !== user.id),
      likes_count: prev.likes_count - 1
    }))
  }

  const remove = () => navigate('/');

  useEffect(() => {
    const fetchPost = async () => {
      setPost({});
      setLoading(true);
      setError('');

      try {
        const data = await getPost(postId);
        setPost(data);
      }
      catch (error) {
        setError(error.message);
      }
      finally {
        setLoading(false);
      }
    }

    fetchPost();
  }, [postId]);

  if (loading) return (<>
    <div className="text-center">
      <div className="spinner-border" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>      
    </div>
  </>);

  return <Post key={postId} post={post} like={like} unlike={unlike} remove={remove} showReplies={true} />

}

export default PostPage;