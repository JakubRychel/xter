import React, { useState } from 'react';
import { useNavigate } from 'react-router';

function EditProfilePage() {
  const [data, setData] = useState({});
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const handleSubmit = async event => {
    event.preventDefault();

    try {
      await register(data);
      navigate('/');
    }
    catch (error) {
      setError(error.message);
    }
  };

  return (<>

  </>);
}

export default EditProfilePage;