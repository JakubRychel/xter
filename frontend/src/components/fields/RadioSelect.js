import React, { useEffect, useState } from 'react';

function RadioSelect({ id, label, defaultValue=null, options={}, setData }) {
  const [value, setValue] = useState(defaultValue);

  useEffect(() => {
    setValue(defaultValue);
  }, [defaultValue]);

  const handleChange = event => {
    setValue(event.target.value);
    setData(prev => ({...prev, [id]: event.target.value }));
  };

  return (<>
    <fieldset className="mb-3">
      <label className="form-label">{label}</label>

      {Object.entries(options).map(([optionValue, optionLabel]) => (
        <div className="form-check" key={optionValue}>
          <input
            type="radio"
            id={`${id}_${optionValue}`}
            name={id}
            value={optionValue}
            checked={value === optionValue}
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