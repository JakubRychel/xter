import api from './api';

export const getNotifications = async () => {
  const response = await api.get('notifications/');
  return response.data;
};

export const markNotificationAsSeen = async (notificationId) => {
  await api.post(`notifications/${notificationId}/mark_as_seen/`, {});
};

export const markAllNotificationsAsSeen = async () => {
  await api.post('notifications/mark_all_as_seen/', {});
};