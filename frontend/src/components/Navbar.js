import React from 'react';
import { useNavigate } from 'react-router';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router';

function Navbar() {
  const { user, logout } = useAuth();

  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (<>
    <nav className="navbar bg-body-tertiary">
      <div className="container">
        <Link className="navbar-brand" to="/">Xter</Link>
        <div className="d-flex gap-2 align-items-baseline">
          { user && (<>
            Zalogowany jako {user.username}
            <button className="btn btn-primary" onClick={handleLogout}>Wyloguj się</button>
          </>)}
        </div>
      </div>
    </nav>
  </>);
}

export default Navbar;