import React, { useState } from 'react';
import { useNavigate } from 'react-router';
import { register } from '../services/auth';


function RegisterForm() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [error, setError] = useState('');

  const navigate = useNavigate();

  const handleSubmit = async event => {
    event.preventDefault();

    try {
      await register(username, email, password, confirmPassword);
      navigate('/login');
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
        <label htmlFor="password2Input" className="form-label">Powtórz hasło</label>
        <input
          type="password"
          id="password2Input"
          className="form-control"
          onChange={event => setConfirmPassword(event.target.value)}
        />
      </div>
      <div className="mb-3">
        <label htmlFor="emailInput" className="form-label">Adres e-mail</label>
        <input
          type="email"
          id="emailInput"
          className="form-control"
          onChange={event => setEmail(event.target.value)}
        />
      </div>
      <div className="mb-3">
        <button type="submit" className="btn btn-primary">Zarejestruj się</button>
      </div>

    </form>
  </>);
}

export default RegisterForm;