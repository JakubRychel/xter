import api from './api';

export const login = async (username, password) => {
  const response = await api.post('auth/login/', { username, password });
  return response.data;
};

export const register = async (username, email, password, password2) => {
  const response = await api.post('auth/register/', { username, email, password, password2 });
  return response.data;
};

export const refresh = async token => {
  const response = await api.post('auth/token/refresh/', { refresh: token });
  return response.data;
};

export const getCurrentUser = async token => {
  const response = await api.get('auth/current-user/');
  return response.data;
}