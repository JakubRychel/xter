import React, { useState } from 'react';
import { useNavigate } from 'react-router';
import { register } from '../services/auth';
import FormField from './fields/FormField';
import ImageField from './fields/ImageField';
import TextareaField from './fields/TextareaField';
import RadioSelect from './fields/RadioSelect';


function RegisterForm() {
  const [data, setData] = useState({});
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const handleSubmit = async event => {
    event.preventDefault();

    try {
      await register(data);
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
      <FormField
        type="password"
        id="password2"
        label="Powtórz hasło"
        setData={setData}
      />
      <FormField
        type="email"
        id="email"
        label="Adres e-mail"
        setData={setData}
      />
      <RadioSelect
        id="gender"
        label="Płeć"
        options={{
          male: 'Mężczyzna',
          female: 'Kobieta'
        }}
        setData={setData}
      />
      <ImageField
        id="profile_picture"
        label="Zdjęcie Profilowe"
        setData={setData}
      />
      <FormField
        id="displayed_name"
        label="Nazwa wyświetlana"
        setData={setData}
      />
      <TextareaField
        id="bio"
        label="Biogram"
        setData={setData}
      />

      <div className="mb-3">
        <button type="submit" className="btn btn-primary">Zarejestruj się</button>
      </div>

    </form>
  </>);
}

export default RegisterForm;