import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoginForm from '../components/LoginForm';
import { Link, NavLink, Outlet } from 'react-router';

function MainPage() {
  const { user, loading } = useAuth();

  if (loading) return (<>
    <div className="text-center">
      <div className="spinner-border" role="status">
        <span className="visually-hidden">Ładowanie...</span>
      </div>      
    </div>
  </>);

  if (user) return (<>
    <ul className="nav nav-tabs">
      <li className="nav-item flex-fill text-center">
        <NavLink to="/recommended" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>Polecane</NavLink>
      </li>
      <li className="nav-item flex-fill text-center">
        <NavLink to="/followed" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>Śledzeni</NavLink>
      </li>
    </ul>

    <Outlet />
  </>)
  
  return (<>
    <LoginForm />
    Nie masz konta? <Link to="/register">Zarejestruj się</Link>
  </>);
}

export default MainPage;