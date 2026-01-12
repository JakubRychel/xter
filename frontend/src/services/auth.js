import api from './api';

export const login = async userData => {
  const response = await api.post('auth/login/', userData);
  return response.data;
};

export const logout = async () => {
  const response = await api.post('auth/logout/', {}, { _noRetry: true });
  return response.data;
}

export const register = async userData => {
  const response = await api.post('auth/register/', userData);
  return response.data;
};

export const refresh = async () => {
  const response = await api.post('auth/token/refresh/', {}, { _noRetry: true });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('auth/current-user/');
  return response.data;
}