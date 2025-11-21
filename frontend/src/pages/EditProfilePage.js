import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { editProfile } from '../services/users';
import FormField from '../components/fields/FormField';
import ImageField from '../components/fields/ImageField';
import TextareaField from '../components/fields/TextareaField';
import RadioSelect from '../components/fields/RadioSelect';

function EditProfilePage() {
  const [data, setData] = useState({});
  const [error, setError] = useState('');

  const { user } = useAuth();

  const handleSubmit = async event => {
    event.preventDefault();

    try {
      await editProfile(data);
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

      <RadioSelect
        id="gender"
        label="Płeć"
        defaultValue={user?.gender}
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
        defaultValue={user?.displayed_name}
        setData={setData}
      />
      <TextareaField
        id="bio"
        label="Biogram"
        defaultValue={user?.bio}
        setData={setData}
      />

      <div className="mb-3">
        <button type="submit" className="btn btn-primary">Zapisz</button>
      </div>

    </form>
  </>);
}

export default EditProfilePage;