import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { deletePost, likePost, unlikePost } from '../services/posts';
import { Link } from 'react-router';
import Feed from './Feed';

function Post({ post, like=null, unlike=null, remove=null, showReplies=false, isReply=false }) {
  const { user } = useAuth();

  const [error, setError] = useState('');

  const handleLike = () => {
    const token = localStorage.getItem('access');

    likePost(post.id, token)
      .then(() => like(post.id))
      .catch(error => console.error(error));
  };

  const handleUnlike = () => {
    const token = localStorage.getItem('access');

    unlikePost(post.id, token)
      .then(() => unlike(post.id))
      .catch(error => console.error(error));
  };

  const handleDelete = () => {
    const token = localStorage.getItem('access');

    deletePost(post.id, token)
      .then(() => remove(post.id))
      .catch(error => console.error(error));
  };

  return(<>
    <div className="card mb-3">
      
      <div className="card-header">
        <h5 className="card-title">{post.author}</h5>
        <div>{post.published_at}</div>        
      </div>

      <div className="card-body">
        {post.content}

        {post.parent && !isReply && <Post key={post.parent.id} post={post.parent} />}
      </div>

      {post.likes && (<>
        <div className="card-footer d-flex gap-2 align-items-baseline">
          
          {post.likes.includes(user.id) ? (<>
            <button
              className="btn rounded-pill d-inline-block btn-primary"
              onClick={handleUnlike}
            >
              <i className="bi bi-heart-fill"></i> {post.likes_count}
            </button>
          </>) : (<>
            <button
              className="btn rounded-pill d-inline-block btn-outline-secondary"
              onClick={handleLike}
            >
              <i className="bi bi-heart-fill"></i> {post.likes_count}
            </button>
          </>)}

          <Link
            className="btn rounded-pill d-inline-block btn-outline-secondary"
            to={`/post/${post.id}`}
          >
            <i className="bi bi-chat-fill"></i> {post.replies_count}
          </Link>

          {user.id === post.author_id && (<>
            <button
              className="btn rounded-pill d-inline-block btn-outline-danger ms-auto"
              data-bs-toggle="modal"
              data-bs-target={`#deletePostModal${post.id}`}
            >
              <i className="bi bi-trash3-fill"></i> usuń
            </button>

            <div className="modal fade" id={`deletePostModal${post.id}`} tabIndex="-1">
              <div className="modal-dialog">
                <div className="modal-content">
                  <div className="modal-header">
                    <h1 className="modal-title fs-5" id="exampleModalLabel">Potwierdź</h1>
                    <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                  </div>
                  <div className="modal-body">
                    Czy na pewno chcesz usunąć post?
                  </div>
                  <div className="modal-footer">
                    <button type="button" className="btn btn-danger" data-bs-dismiss="modal" onClick={handleDelete}>Tak</button>
                    <button type="button" className="btn btn-outline-secondary" data-bs-dismiss="modal">Nie</button>
                  </div>
                </div>
              </div>
            </div>
          </>)}
        </div>
      </>)}
      
      {showReplies && (
        <div className="card-body">
          <Feed data={post.replies} parent={post.id} />
        </div>
      )}

    </div>
  </>);
}

export default Post;