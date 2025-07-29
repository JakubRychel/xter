import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { deletePost, likePost, unlikePost } from '../services/posts';

function Post({ id, children, author, authorId, time, liked=false, likes=0, deleteFromFeed }) {
  const { user } = useAuth();

  const [isLiked, setIsLiked] = useState(liked);

  const handleLike = () => {
    setIsLiked(prev => {
      const token = localStorage.getItem('access');

      prev ? unlikePost(id, token) : likePost(id, token);
      return !prev;
    });
  };

  const handleDelete = () => {
    const token = localStorage.getItem('access');
    deletePost(id, token)
      .then(response => deleteFromFeed(id))
      .catch(error => console.error(error));
  };

  return(<>
    <div className="card my-2">
      <div className="card-header">
        <h5 className="card-title">{author}</h5>
        <div>{time}</div>        
      </div>
      <div className="card-body">
        {children}
      </div>
      <div className="card-footer d-flex gap-2 align-items-baseline">
        <button
          className={'btn btn-sm d-inline-block ' + (isLiked ? 'btn-primary' : 'btn-outline-primary')}
          onClick={handleLike}
        >
          {isLiked
            ? <><i className="bi bi-heartbreak-fill"></i> Jednak nie lubię</>
            : <><i className="bi bi-heart-fill"></i> Lubię to</>
          }
        </button>
        Lubi to {likes + (liked ? -1 : 0) + (isLiked ? 1 : 0)} osób
        { user.id === authorId && (<>
          <button
            className="btn btn-sm d-inline-block btn-outline-danger"
            data-bs-toggle="modal"
            data-bs-target={`#deletePostModal${id}`}
          >Usuń post</button>

          <div className="modal fade" id={`deletePostModal${id}`} tabIndex="-1">
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
    </div>
  </>);
}

export default Post;