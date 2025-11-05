import React, { useRef, useState } from 'react';
import { createPost, updatePost } from '../services/posts';

function CreatePostForm({ parent=null, setEditing=null, submitToFeed, post=null }) {
  const [content, setContent] = useState(post?.content || '');
  const [error, setError] = useState('');

  const [sending, setSending] = useState(false);
  const [progress, setProgress] = useState('1%');

  const timerRef = useRef(null);

  const handleCreate = async () => {
    const createdPost = await createPost({ content, parent_id: parent });
    submitToFeed(createdPost);
  }

  const handleUpdate = async () => {
    const updatedPost = await updatePost(post.id, { content });
    submitToFeed(post.id, updatedPost);
  };

  const submit = async () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    setSending(true);

    try {
      post ? await handleUpdate() : await handleCreate();
      setProgress('100%');

      timerRef.current = setTimeout(() => {
        setSending(false);
        setContent('');
        setProgress('1%');
        if (setEditing) setEditing(false);
        timerRef.current = null;
      }, 200);
    }
    catch (error) {
      setSending(false);
      setContent('');
      setProgress('1%');
      if (setEditing) setEditing(false);
      setError(error.message);
    }
  }

  const handleSubmit = event => {
    event.preventDefault();
    submit();
  };

  const handleKeyDown = event => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };


	return (<>
		<form onSubmit={handleSubmit} onClick={event => event.stopPropagation()}>

      {error && (<>
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      </>)}

      <div className="my-3">

        {sending && (<>
          <div className="progress" role="progressbar" style={{height: '5px', marginBottom: '-5px'}}>
            <div 
              className="progress-bar"
              style={{
                width: `${progress}`,
                transition: 'width .2s ease-in-out'
              }}
            ></div>
          </div>
        </>)}
        
        <textarea
          placeholder="Napisz coś..."
          className="form-control"
          rows="3"
          value={content}
          onChange={event => setContent(event.target.value)}
          onKeyDown={handleKeyDown}
          disabled={sending}
        />

      </div>
      <div className="my-3">
        <button type="submit" className="btn btn-primary">Wyślij</button>
      </div>
		</form>
	</>);
}

export default CreatePostForm;