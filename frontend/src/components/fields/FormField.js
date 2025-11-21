import React from 'react';

function FormField({ type='text', id, label, defaultValue, setData }) {
  const handleChange = event => {
    setData(prev => ({...prev, [id]: event.target.value }))
  };

  return (<>
    <div className="mb-3">
      <label htmlFor={id + 'Input'} className="form-label">{label}</label>
      <input
        type={type}
        id={id + 'Input'}
        defaultValue={defaultValue}
        className="form-control"
        onChange={handleChange}
      />
    </div>
  </>);
}

export default FormField;