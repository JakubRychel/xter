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
          <ul className="navbar-nav gap-1 align-items-center">
            <li className="nav-item">
              <Notifications />
            </li>
            <li className="nav-item">

              <div className="dropdown">
                <button
                  className="btn btn-outline-secondary dropdown-toggle d-flex gap-2 align-items-center"
                  type="button" data-bs-toggle="dropdown"
                >
                  <ProfilePicture src={user.profile_picture} size="1.2rem" /> {user.displayed_name} (@{user.username})
                </button>
                <ul className="dropdown-menu">
                  <li>
                    <Link to={`/@/${user.username}`} className="dropdown-item">
                      <i className="bi bi-person-fill"></i> Zobacz profil
                    </Link>
                  </li>
                  <li>
                    <Link to="/edit-profile" className="dropdown-item">
                      <i className="bi bi-pencil-fill"></i> Edytuj profil
                    </Link>
                  </li>
                  <li>
                    <button className="dropdown-item" onClick={handleLogout}>
                      <i className="bi bi-door-open-fill"></i> Wyloguj się
                    </button>
                  </li>
                </ul>
              </div>

            </li>
          </ul>
        </>)}

      </div>
    </nav>
  </>);
}

export default Navbar;