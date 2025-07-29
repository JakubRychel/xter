import api from './api';

export const login = async (username, password) => {
  const response = await api.post('users/login/', { username, password });
  return response.data;
};

export const register = async (username, email, password, password2) => {
  const response = await api.post('users/register/', { username, email, password, password2 });
  return response.data;
};

export const refresh = async token => {
  const response = await api.post('users/token/refresh/', { refresh: token });
  return response.data;
};

export const getCurrentUser = async token => {
  const response = await api.get('users/current-user/', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
}