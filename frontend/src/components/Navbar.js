import React from 'react';
import { useNavigate } from 'react-router';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router';
import Notifications from './Notifications';
import ProfilePicture from './ProfilePicture';

function Navbar() {
  const { user, logout } = useAuth();

  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (<>
    <nav className="navbar navbar-expand bg-body-tertiary">
      <div className="container flex-wrap">

        <Link className="navbar-brand" to="/">Xter</Link>

        { user && (<>
          <ul className="navbar-nav gap-3 align-items-center">
            <li className="nav-item">
              <Notifications />
            </li>
            <li className="nav-item">
              Zalogowany jako <ProfilePicture src={user.profile_picture} size="1.2rem" /> {user.displayed_name} (@{user.username})
            </li>
            <li className="nav-item">
              <button className="btn btn-primary" onClick={handleLogout}>Wyloguj się</button>
            </li>
          </ul>
        </>)}

      </div>
    </nav>
  </>);
}

export default Navbar;