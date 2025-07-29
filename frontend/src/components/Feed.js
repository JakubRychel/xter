import React, { useState } from 'react';
import CreatePostForm from '../components/CreatePostForm';
import Post from './Post';
import { useAuth } from '../contexts/AuthContext';


function Feed({ data, parent=null }) {
  const { user } = useAuth();

  const [posts, setPosts] = useState(data);

  const addToFeed = post => {
    setPosts(prev => [post, ...prev]);
  };

  const deleteFromFeed = id => {
    setPosts(prev => prev.filter(post => post.id !== id));
  };

  const likeInFeed = id => {
    setPosts(prev => prev.map(post => post.id === id ? {
      ...post,
      likes: [...post.likes, user.id],
      likes_count: post.likes_count + 1
    } : post))
  }

  const unlikeInFeed = id => {
    setPosts(prev => prev.map(post => post.id === id ? {
      ...post,
      likes: post.likes.filter(like => like !== user.id),
      likes_count: post.likes_count - 1
    } : post))
  }

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
  </>);
}

export default Feed;