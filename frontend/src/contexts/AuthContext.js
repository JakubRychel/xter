import React, { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import { login, refresh, getCurrentUser } from '../services/auth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loginUser = async (username, password) => {
    const data = await login(username, password);
    localStorage.setItem('access', data.access);
    localStorage.setItem('refresh', data.refresh);

    const userData = await getCurrentUser(data.access);
    setUser(userData);
  };

  const logoutUser = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    setUser(null);
  }

  const refreshToken = async () => {
    const token = localStorage.getItem('refresh');

    if (!token) {
      logoutUser();
      return;
    }

    try {
      const data = await refresh(token);
      localStorage.setItem('access', data.access);

      const userData = await getCurrentUser(data.access);
      setUser(userData);
    }
    catch (error) {
      logoutUser();
    }
  }

  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('access');
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const userData = await getCurrentUser(token);
        setUser(userData);
      }
      catch {
        logoutUser();
      }
      finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  useEffect(() => {
    refreshToken();

    const interval = setInterval(() => {
      refreshToken();
    }, 1000 * 60 * 4);

    return () => clearInterval(interval);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login: loginUser, logout: logoutUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);