import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useParams } from 'react-router';
import Feed from '../components/Feed';
import { followUser, unfollowUser, getUser } from '../services/users';

function ProfilePage() {
  const { username } = useParams();

  const { user } = useAuth();

  const [profile, setProfile] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const loadUser = async () => {
    try {
      const data = await getUser(username);

      setProfile(data);
    }
    catch (error) {
      setError(error.message);
    }
    finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUser();
  }, [username]);

  const handleFollow = () => {
    const token = localStorage.getItem('access');

    followUser(profile.username, token)
      .then(() => {
        setProfile(prev => ({
          ...prev,
          followers: [...prev.followers, user.id],
          followers_count: prev.followers_count + 1
        }))
      })
      .catch(error => console.error(error));
  };

  const handleUnfollow = () => {
    const token = localStorage.getItem('access');

    unfollowUser(profile.username, token)
      .then(() => {
        setProfile(prev => ({
          ...prev,
          followers: prev.followers.filter(follower => follower !== user.id),
          followers_count: prev.followers_count - 1
        }))
      })
      .catch(error => console.error(error));
  };

  if (loading) return (<>
    <div className="text-center">
      <div className="spinner-border" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>      
    </div>
  </>);

  return (<>
    <div className="my-3">
      <h5 className="mb-0">
        <span className="fw-semibold">
          {profile.displayed_name}
        </span>
      </h5>
      <span className="text-muted">@{profile.username}</span>

      {profile.bio && <p className="my-2">{profile.bio}</p>}

      <div className="my-3 d-flex gap-2 align-items-baseline">
        {user && profile.followers.includes(user.id) ? (<>
          <button
            className="btn rounded-pill d-inline-block btn-outline-secondary"
            onClick={handleUnfollow}
          >
            Przestań śledzić
          </button>
        </>) : (<>
          <button
            className="btn rounded-pill d-inline-block btn-primary"
            onClick={handleFollow}
          >
            Śledź
          </button>
        </>)}
      </div>
    </div>

    <Feed author={username} />
  </>);
}

export default ProfilePage;