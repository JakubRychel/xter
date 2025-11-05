import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { deletePost, likePost, unlikePost, updatePost, readPost } from '../services/posts';
import CreatePostForm from './CreatePostForm';
import { Link, useNavigate } from 'react-router';
import Feed from './Feed';

function Post({ post, like=null, unlike=null, update=null, remove=null, read=null, showReplies=false, isReply=false }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const contentRef = useRef(null);

  const [editing, setEditing] = useState(false);

  const handleLike = () => {
    likePost(post.id)
      .then(() => like(post.id))
      .catch(error => console.error(error));
  };

  const handleUnlike = () => {
    unlikePost(post.id)
      .then(() => unlike(post.id))
      .catch(error => console.error(error));
  };

  const handleDelete = () => {
    deletePost(post.id)
      .then(() => remove(post.id))
      .catch(error => console.error(error));
  };

  const handleRead = () => {
    readPost(post.id)
      .then(() => read(post.id))
      .catch(error => console.error(error));
  }

  useEffect(() => {
    if (!user) return;
    if (post.read_by.includes(user.id)) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          handleRead();
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    if (contentRef.current) observer.observe(contentRef.current);

    return () => {
      if (contentRef.current) observer.unobserve(contentRef.current);
    };
  }, [post.id, user?.id, post.read_by]);

  return(<>
    <div className="card my-3" onClick={event => event.stopPropagation()}>
      
      <div className="card-header">
        <h5 className="card-title d-inline-flex gap-1 align-items-baseline">
          <Link className="link-dark" to={`/@/${post.author_username}/`}>
            <span className="fw-semibold">
              {post.author_displayed_name}
            </span>
          </Link>
          <span className="text-muted">@{post.author_username}</span>
        </h5>
        <div>{post.published_at}</div>
      </div>

      <div className="card-body py-0">
        <div ref={contentRef} className="my-3" role="button" onClick={() => navigate(`/post/${post.id}/`)}>
          {editing ? <CreatePostForm setEditing={setEditing} submitToFeed={update} post={post} /> : post.content}
        </div>

        {post.parent && !isReply && <Post post={post.parent} read={read} />}

        {post.liked_by && user && (<>
          <div className="my-3 d-flex gap-2 align-items-baseline">
            
            {post.liked_by.includes(user.id) ? (<>
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
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              data-bs-title="Odpowiedz"
            >
              <i className="bi bi-chat-fill"></i> {post.replies_count}
            </Link>

            {user && user.id === post.author_id && (<>
              <button
                className={`btn rounded-pill d-inline-block ${editing ? 'btn-primary' : 'btn-outline-secondary'} ms-auto`}
                onClick={() => setEditing(prev => !prev)}
              >
                <i className="bi bi-pencil-fill"></i> edytuj
              </button>

              <button
                className="btn rounded-pill d-inline-block btn-outline-danger"
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

        {showReplies && <Feed parent={post.id} />}
      </div>

    </div>
  </>);
}

export default Post;