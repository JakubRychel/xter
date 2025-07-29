import React, { useState } from 'react';

function NestedPost({ children, author, time }) {
  return(<>
    <div className="card my-2">
      <div className="card-header">
        <h5 className="card-title">{author}</h5>
        <div>{time}</div>        
      </div>
      <div className="card-body">
        {children}
      </div>
    </div>
  </>);
}

export default NestedPost;