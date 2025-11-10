import React, { createContext, useContext, useState, useEffect, useLayoutEffect } from 'react';
import api from '../services/api';
import { login, logout, refresh, getCurrentUser } from '../services/auth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loginUser = async (username, password) => {
    const data = await login(username, password);
    setToken(data.access);

    const userData = await getCurrentUser();
    setUser(userData);
  }

  const logoutUser = () => {
    logout();
    setToken(null);
    setUser(null);
  }

  const refreshToken = async () => {
    try {
      const data = await refresh();
      setToken(data.access);
      return data.access;
    }
    catch (error) {
      //logoutUser();
      throw error;
    }
  }

  const connectWebSocket = path => {
    const url = `ws://${window.location.host}/ws/${path}/`;

    const createWS = currentToken => {
      return new WebSocket(url, currentToken);
    };

    let ws = createWS(token);

    ws.onopen = event => console.log("WebSocket OPEN:", event);
    ws.onmessage = event => console.log("WebSocket MESSAGE:", event.data);
    ws.onerror = event => console.error("WebSocket ERROR:", event);
    ws.onclose = async event => {
      console.log("WebSocket CLOSE:", event);
      if (event.code === 4001) {
        try {
          const newToken = await refreshToken();
          ws = createWS(newToken);
        }
        catch (error) {
          console.error('WebSocket reconnection failed:', error);
        }
      }
    };

    return ws;
  };

  useLayoutEffect(() => {
    const authInterceptor = api.interceptors.request.use(config => {

      if (token && !config._noRetry) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });

    return () => {
      api.interceptors.request.eject(authInterceptor);
    }
  }, [token]);

  useLayoutEffect(() => {
    const refreshInterceptor = api.interceptors.response.use(response => response, async error => {

      const originalRequest = error.config;

      if (error.response.status === 401 && !originalRequest._noRetry) {
        try {
          const newToken = await refreshToken();
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          originalRequest._noRetry = true;

          return api(originalRequest);
        }
        catch (refreshError) {
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    });

    return () => {
      api.interceptors.response.eject(refreshInterceptor);
    }
  }, []);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
        setLoading(false);
      }
      catch (error) {
        //logoutUser();
        setLoading(false);
        throw error;
      }
    }
    loadUser();
  }, []);

  return (
    <AuthContext.Provider value={{ connectWebSocket, user, login: loginUser, logout: logoutUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);