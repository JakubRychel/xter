import api from './api';

export const getUsers = async () => {
  const response = await api.get('users/');
  return response.data;
};

export const getUser = async userId => {
  const response = await api.get(`users/${userId}/`);
  return response.data;
};

export const followUser = async username => {
  const response = await api.post(`users/${username}/follow/`, {})
};

export const unfollowUser = async username => {
  const response = await api.post(`users/${username}/unfollow/`, {})
};

export const editProfile = async data => {
  const formData = new FormData();

  Object.entries(data).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      formData.append(key, value);
    }
  });

  for (let pair of formData.entries()) {
    console.log(pair[0], pair[1]);
  }

  const response = await api.patch('user/edit-profile/', formData);

  return response.data;
};

export const changePassword = async (oldPassword, password, password2) => {
  const response = await api.patch('user/change-password/', { old_password: oldPassword, password, password2 });
  return response.data;
};