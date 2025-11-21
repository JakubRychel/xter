import React from 'react';

function RadioSelect({ id, label, options={}, setData }) {
  const handleChange = event => {
    setData(prev => ({...prev, [id]: event.target.value }))
  };

  return (<>
    <fieldset className="mb-3">
      <legend className="form-label">{label}</legend>

      {Object.entries(options).map(([optionValue, optionLabel]) => (
        <div className="form-check" key={optionValue}>
          <input
            type="radio"
            id={`${id}_${optionValue}`}
            name={id}
            value={optionValue}
            className="form-check-input"
            onChange={handleChange}
          />
          <label
            className="form-check-label"
            htmlFor={`${id}_${optionValue}`}
          >
            {optionLabel}
          </label>
        </div>
      ))}
    </fieldset>
  </>);
}

export default RadioSelect;