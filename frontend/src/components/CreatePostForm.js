import React, { useState } from 'react';
import { createPost } from '../services/posts';

function CreatePostForm({ parent=null, addToFeed }) {
  const [content, setContent] = useState('');

  const [error, setError] = useState('');

  const submit = async () => {
    const token = localStorage.getItem('access');
    const postData = { content, parent_id: parent };

    try {
      const post = await createPost(postData, token);
      addToFeed(post);
      setContent('');
    }
    catch (error) {
      setError(error.message);
    }
  };

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
        <textarea
          placeholder="Napisz coś"
          className="form-control"
          rows="3"
          value={content}
          onChange={event => setContent(event.target.value)}
          onKeyDown={handleKeyDown}
        />
      </div>
      <div className="my-3">
        <button type="submit" className="btn btn-primary">Wyślij</button>
      </div>
		</form>
	</>);
}

export default CreatePostForm;