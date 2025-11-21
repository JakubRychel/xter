import React from 'react';

function ProfilePicture({ src, size='3rem' }) {
  return (
    <div
      className="d-inline-flex justify-content-center align-items-center"
      style={{width: size, height: size}}
    >
      <img src={src} alt="profile_picture" className="rounded-circle w-100 h-100" />
    </div>
  );
}

export default ProfilePicture;