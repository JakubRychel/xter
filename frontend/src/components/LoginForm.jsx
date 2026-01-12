import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router';
import FormField from './fields/FormField';


function LoginForm() {
  const [data, setData] = useState({});
  const [error, setError] = useState('');

  const { login } = useAuth();

  const navigate = useNavigate();

  const handleSubmit = async event => {
    event.preventDefault();

    try {
      await login(data);
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

      <FormField
        id="username"
        label="Nazwa użytkownika"
        setData={setData}
      />
      <FormField
        type="password"
        id="password"
        label="Hasło"
        setData={setData}
      />

      <div className="mb-3">
        <button type="submit" className="btn btn-primary">Zaloguj się</button>
      </div>

    </form>
  </>);
}

export default LoginForm;