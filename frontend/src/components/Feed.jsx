import React, { useState, useEffect, useRef } from 'react';
import CreatePostForm from '../components/CreatePostForm';
import Post from './Post';
import { useAuth } from '../contexts/AuthContext';
import { getPosts } from '../services/posts';


function Feed({ author = null, parent = null, followed = false }) {
  const feedRef = useRef(null);
  const { user } = useAuth();

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [nextPage, setNextPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const addToFeed = post => {
    setPosts(prev => [post, ...prev]);
  };

  const updateInFeed = (id, postData) => {
    setPosts(prev => prev.map(post => post.id === id ? {
      ...post,
      ...postData
    } : post));
  };

  const deleteFromFeed = id => {
    setPosts(prev => prev.filter(post => post.id !== id));
  };

  const likeInFeed = id => {
    setPosts(prev => prev.map(post => post.id === id ? {
      ...post,
      liked_by: [...post.liked_by, user.id],
      likes_count: post.likes_count + 1
    } : post));
  };

  const unlikeInFeed = id => {
    setPosts(prev => prev.map(post => post.id === id ? {
      ...post,
      liked_by: post.liked_by.filter(like => like !== user.id),
      likes_count: post.likes_count - 1
    } : post));
  };

  const readInFeed = id => {
    setPosts(prev => prev.map(post => {
      if (post.id === id) return {
        ...post,
        read_by: [...post.read_by, user.id],
        reads_count: post.reads_count + 1
      }
      else if (post.parent && post.parent.id === id) return {
        ...post,
        parent: {
          ...post.parent,
          read_by: [...post.parent.read_by, user.id],
          reads_count: post.parent.reads_count + 1
        }
      }
      else return post;
    }));
  };

  const loadPosts = async (page = 1) => {
    if (loading || !hasMore) return;

    setLoading(true);

    try {
      const data = await getPosts(author, parent, followed, page);

      setPosts(prev => page === 1 ? data.results : [...prev, ...data.results]);
      setNextPage(page + 1);
      setHasMore(Boolean(data.next));
      setLoading(false);
    }
    catch (error) {
      setError(error.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    setPosts([]);
    setNextPage(1);
    setHasMore(true);
    loadPosts();
  }, [author, parent, followed]);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight;
      const clientHeight = window.innerHeight;

      if (scrollTop + clientHeight >= scrollHeight - 1 && !loading && hasMore) {
        loadPosts(nextPage);
      }
    };

    window.addEventListener('scroll', handleScroll);

    return () => window.removeEventListener('scroll', handleScroll);
  }, [loading, nextPage, hasMore]);

  return (
    <>
      {!author && <CreatePostForm parent={parent} submitToFeed={addToFeed} />}

      {posts && posts.map(post => (
        <Post
          key={post.id}
          post={post}
          like={likeInFeed}
          unlike={unlikeInFeed}
          update={updateInFeed}
          remove={deleteFromFeed}
          read={readInFeed}
          isReply={!!parent}
        />
      ))}

      {loading && (
        <div className="text-center my-3">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Ładowanie...</span>
          </div>
        </div>
      )}

      {!hasMore && !loading && posts.length > 0 && (
        <div className="text-center my-3 text-muted">Nie ma więcej postów</div>
      )}
    </>
  );
}

export default Feed;
