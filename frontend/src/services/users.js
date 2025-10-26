import api from './api';

export const getUsers = async () => {
  const response = await api.get('users/');
  return response.data;
};

export const getUser = async userId => {
  const response = await api.get(`users/${userId}/`);
  return response.data;
}

export const followUser = async (username, token) => {
  const response = await api.post(`users/${username}/follow/`, {})
}

export const unfollowUser = async (username, token) => {
  const response = await api.post(`users/${username}/unfollow/`, {})
}