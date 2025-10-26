import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoginForm from '../components/LoginForm';
import { Link, NavLink, Outlet } from 'react-router';
import Feed from '../components/Feed';

function MainPage() {
  const { user } = useAuth();

  return user ? (<>
    <ul className="nav nav-tabs">
      <li className="nav-item flex-fill text-center">
        <NavLink to="/popular" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>Popularne</NavLink>
      </li>
      <li className="nav-item flex-fill text-center">
        <NavLink to="/followed" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>Śledzeni</NavLink>
      </li>
    </ul>

    <Outlet />

  </>) : (<>
    <LoginForm />
    Nie masz konta? <Link to="/register">Zarejestruj się</Link>
  </>);
}

export default MainPage;