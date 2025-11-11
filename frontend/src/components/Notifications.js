import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router';
import { getNotifications, markNotificationAsSeen, markAllNotificationsAsSeen } from '../services/notifications';

function Notification({ notification }) {
  const navigate = useNavigate();

  const handleNotificationClick = event => {
    markNotificationAsSeen(notification.id)
      .catch(error => console.error(error));
  }

  switch (notification.notification_type) {
    case 'reply':
      return (<>
        <li className="dropdown-item">
          <span
            className="dropdown-item-text"
            onClick={event => {
              handleNotificationClick(event);
              navigate(`/post/${notification.related_post.id}`);
            }}
          >
            <Link to={`/@/${notification.events[0].actor.username}`} onClick={event => event.stopPropagation()}>
              {notification.events[0].actor.username}
            </Link> odpowiedział(a) na Twój post: <span className="fw-bold">
              {notification.related_post?.content.slice(0, 30)}{notification.related_post?.content.length > 30 ? '...' : ''}
            </span>
          </span>
        </li>
      </>);
    case 'like':
      return (<>
        <li className="dropdown-item">
          <span
            className="dropdown-item-text"
            onClick={event => {
              handleNotificationClick(event);
              navigate(`/post/${notification.related_post.id}`);
            }}
          >
            <Link to={`/@/${notification.events[0].actor.username}`} onClick={event => event.stopPropagation()}>
              {notification.events[0].actor.username}
            </Link> polubił(a) Twój post: <span className="fw-bold">
              {notification.related_post?.content.slice(0, 30)}{notification.related_post?.content.length > 30 ? '...' : ''}
            </span>
          </span>
        </li>
      </>);
    case 'follow':
      return (<>
        <li className="dropdown-item">
          <span
            className="dropdown-item-text"
            onClick={event => {
              handleNotificationClick(event);
              navigate(`/@/${notification.events[0].actor.username}`);
            }}  
          >
            <Link to={`/@/${notification.events[0].actor.username}`} onClick={event => event.stopPropagation()}>
              {notification.events[0].actor.username}
            </Link> zaczął(a) Cię obserwować 
          </span>
        </li>
      </>);
    case 'mention':
      return (<>
        <li className="dropdown-item">
          <span
            className="dropdown-item-text"
            onClick={event => {
              handleNotificationClick(event);
              navigate(`/post/${notification.related_post.id}`);
            }}  
          >
            <Link to={`/@/${notification.events[0].actor.username}`} onClick={event => event.stopPropagation()}>
              {notification.events[0].actor.username}
            </Link> wspomniał(a) Cię w poście: <span className="fw-bold">
              {notification.related_post?.content.slice(0, 30)}{notification.related_post?.content.length > 30 ? '...' : ''}
            </span>
          </span>
        </li>
      </>);
    case 'followed_user_posted':
      return (<>
        <li className="dropdown-item">
          <span
            className="dropdown-item-text"
            onClick={event => {
              handleNotificationClick(event);
              navigate(`/post/${notification.related_post.id}`);
            }}  
          >
            <Link to={`/@/${notification.events[0].actor.username}`} onClick={event => event.stopPropagation()}>
              {notification.events[0].actor.username}
            </Link> opublikował(a) nowy post: <span className="fw-bold">
              {notification.related_post?.content.slice(0, 30)}{notification.related_post?.content.length > 30 ? '...' : ''}
            </span>
          </span>
        </li>
      </>);
  }
}

function Notifications() {
  const [notifications, setNotifications] = useState(null);
  const [loading, setLoading] = useState(true);

  const { connectWebSocket } = useAuth();

  const mergeNotifications = (notifications, newNotification) => {
    const exists = notifications.find(n => n.id === newNotification.id);

    if (exists) {
      return notifications.map(n => n.id === newNotification.id ? newNotification : n);
    }
    else {
      return [newNotification, ...notifications];
    }
  };

  useEffect(() => {
    console.log('Notifications updated:', notifications);
  }, [notifications]);

  useEffect(() => {
    const fetchNotifications = async () => {
      const notifications = await getNotifications();

      setNotifications(notifications);
      setLoading(false);
    };

    fetchNotifications();

    const ws = connectWebSocket('notifications');

    ws.onmessage = event => {
      const newNotification = JSON.parse(event.data);

      console.log('Received notification via WebSocket:', newNotification);

      setNotifications(notifications => mergeNotifications(notifications, newNotification));
    };

    return () => ws.close();
  }, [connectWebSocket]);

  return (<>
    <div className="dropdown">
      <button className="btn btn-primary" type="button" data-bs-toggle="dropdown">
        <i className="bi bi-bell-fill"></i>
          {notifications && notifications.length > 0 && <>
            <span className="position-absolute top-0 start-100 translate-middle badge p-1 rounded-pill bg-danger">
              {notifications.length}
              <span className="visually-hidden">powiadomienia</span>
            </span>
          </>}
      </button>
      <ul className="dropdown-menu">
        {loading ? (<>
          <li className="dropdown-item">
            <div className="text-center dropdown-item-text">
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Ładowanie...</span>
              </div>      
            </div>
          </li>
        </>) : notifications && notifications.map(notification => <Notification key={notification.id} notification={notification} />)}
      
      </ul>
    </div>
  </>);
}

export default Notifications;