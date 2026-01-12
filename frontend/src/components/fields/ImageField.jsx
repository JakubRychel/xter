import React from 'react';

function ImageField({ id, label, setData }) {
  const handleChange = event => {
    setData(prev => ({...prev, [id]: event.target.files[0] || null }))
  };

  return (<>
    <div className="mb-3">
      <label htmlFor={id + 'Input'} className="form-label">{label}</label>
      <input
        type="file"
        id={id + 'Input'}
        className="form-control"
        accept="image/*"
        onChange={handleChange}
      />
    </div>
  </>);
}

export default ImageField;