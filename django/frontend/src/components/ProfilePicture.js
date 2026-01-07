import React from 'react';

function ProfilePicture({ src, size='3rem' }) {
  return (
    <img
      src={src}
      alt="profile_picture"
      className="rounded-circle"
      style={{height: size, aspectRatio: '1 / 1', objectFit: 'cover'}}
    />
  );
}

export default ProfilePicture;