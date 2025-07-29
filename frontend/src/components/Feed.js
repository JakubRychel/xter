import React, { useEffect, useState } from 'react';
import { getPosts } from '../services/posts';
import CreatePostForm from '../components/CreatePostForm';
import Post from './Post';
import NestedPost from './NestedPost';
import { useAuth } from '../contexts/AuthContext';


function Feed() {
  const { user } = useAuth();

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const addToFeed = post => {
    setPosts(prev => [post, ...prev]);
  };

  const deleteFromFeed = id => {
    setPosts(prev => prev.filter(post => post.id !== id));
  };

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

  return (<>
    <CreatePostForm addToFeed={addToFeed} />

    {posts && posts.map(post => (
      <Post
        key={post.id}
        id={post.id}
        author={post.author}
        authorId={post.author_id}
        time={post.published_at}
        liked={post.likes.includes(user.id)}
        likes={post.likes_count}
        deleteFromFeed={deleteFromFeed}
      >
        {post.content}
        {post.parent && (
          <NestedPost
            key={post.parent.id}
            author={post.parent.author}
            time={post.parent.time}
          >
            {post.parent.content}
          </NestedPost>
        )}
      </Post>
    ))}
  </>);
}

export default Feed;