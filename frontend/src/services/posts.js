import api from './api';

export const getPosts = async (author = null, parent = null, followed = false, page = 1) => {
  const params = new URLSearchParams();

  if (author) params.append('author', author);
  else if (parent) params.append('parent_id', parent);
  else if (followed) params.append('followed', 'true');
  if (page) params.append('page', page);

  const response = await api.get('posts/' + (params.toString() ? '?' + params.toString() : ''));
  return response.data;
};

export const getPost = async (postId) => {
  const response = await api.get(`posts/${postId}/`);
  return response.data;
};

export const createPost = async (postData) => {
  const response = await api.post('posts/', postData);
  return response.data;
};

export const deletePost = async (postId) => {
  await api.delete(`posts/${postId}/`, {});
};

export const likePost = async (postId) => {
  await api.post(`posts/${postId}/like/`, {});
};

export const unlikePost = async (postId) => {
  await api.post(`posts/${postId}/unlike/`, {});
};

export const readPost = async (postId) => {
  await api.post(`posts/${postId}/read/`, {});
};