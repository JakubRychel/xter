import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router';


function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const [error, setError] = useState('');

  const { login } = useAuth();

  const navigate = useNavigate();

  const handleSubmit = async event => {
    event.preventDefault();

    try {
      await login(username, password);
      navigate('/');
    }
    catch (error) {
      setError(error.message);
    }
  };

  return (<>
    <form onSubmit={handleSubmit}>

      {error && (<>
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      </>)}

      <div className="mb-3">
        <label htmlFor="usernameInput" className="form-label">Nazwa użytkownika</label>
        <input
          type="text"
          id="usernameInput"
          className="form-control"
          onChange={event => setUsername(event.target.value)}
        />
      </div>
      <div className="mb-3">
        <label htmlFor="passwordInput" className="form-label">Hasło</label>
        <input
          type="password"
          id="passwordInput"
          className="form-control"
          onChange={event => setPassword(event.target.value)}
        />
      </div>
      <div className="mb-3">
        <button type="submit" className="btn btn-primary">Zaloguj się</button>
      </div>

    </form>
  </>);
}

export default LoginForm;