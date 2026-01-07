import React from 'react';

function TextareaField({ id, label, defaultValue, setData, rows=4 }) {
  const handleChange = event => {
    setData(prev => ({...prev, [id]: event.target.value }))
  };

  return (<>
    <div className="mb-3">
      <label htmlFor={id + 'Input'} className="form-label">{label}</label>
      <textarea
        id={id + 'Input'}
        defaultValue={defaultValue}
        className="form-control"
        onChange={handleChange}
        rows={rows}
      />
    </div>
  </>);
}

export default TextareaField;