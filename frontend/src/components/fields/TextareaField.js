import React from 'react';

function TextareaField({ id, label, setData, rows=4 }) {
  const handleChange = event => {
    setData(prev => ({...prev, [id]: event.target.value }))
  };

  return (<>
    <div className="mb-3">
      <label htmlFor={id + 'Input'} className="form-label">{label}</label>
      <textarea
        id={id + 'Input'}
        className="form-control"
        onChange={handleChange}
        rows={rows}
      />
    </div>
  </>);
}

export default TextareaField;