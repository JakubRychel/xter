import React, { useRef, useState } from 'react';
import { createPost } from '../services/posts';

function CreatePostForm({ parent=null, addToFeed }) {
  const [content, setContent] = useState('');
  const [error, setError] = useState('');

  const [sending, setSending] = useState(false);
  const [progress, setProgress] = useState('1%');

  const timerRef = useRef(null);

  const submit = async () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    setSending(true);

    const postData = { content, parent_id: parent };

    try {
      const post = await createPost(postData);
      addToFeed(post);
      setProgress('100%');

      timerRef.current = setTimeout(() => {
        setSending(false);
        setContent('');
        setProgress('1%');
        timerRef.current = null;
      }, 300);
    }
    catch (error) {
      setSending(false);
      setContent('');
      setProgress('1%');
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
		<form onSubmit={handleSubmit}>

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
                transition: 'width .3s ease-in-out'
              }}
            ></div>
          </div>
        </>)}
        
        <textarea
          placeholder="Napisz coś"
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