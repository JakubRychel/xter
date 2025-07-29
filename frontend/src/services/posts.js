import api from './api';

export const getPosts = async () => {
  const response = await api.get('posts/');
  return response.data;
};

export const getPost = async postId => {
  const response = await api.get(`posts/${postId}/`);
  return response.data;
}

export const createPost = async (postData, token) => {
  const response = await api.post('posts/', postData, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export const deletePost = async (postId, token) => {
  const response = await api.delete(`posts/${postId}/`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
};

export const likePost = async (postId, token) => {
  const response = await api.post(`posts/${postId}/like/`, {}, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
}

export const unlikePost = async (postId, token) => {
  const response = await api.post(`posts/${postId}/unlike/`, {}, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
}