import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router';
import { getNotifications, markNotificationAsSeen, markAllNotificationsAsSeen } from '../services/notifications';

function Notification({ notification }) {
  switch (notification.notification_type) {
    case 'reply':
      return (<>
        <Link to={`/@/${notification.events[0].actor.username}`} onClick={event => event.stopPropagation()}>
          {notification.events[0].actor.displayed_name} (@{notification.events[0].actor.username})
        </Link> odpowiedział(a) na Twój post: <span className="fst-italic">
          {notification.related_post?.content.slice(0, 30)}{notification.related_post?.content.length > 30 ? '...' : ''}
        </span>
      </>);
    case 'like':
      return (<>
        <Link to={`/@/${notification.events[0].actor.username}`} onClick={event => event.stopPropagation()}>
          {notification.events[0].actor.displayed_name} (@{notification.events[0].actor.username})
        </Link> polubił(a) Twój post: <span className="fst-italic">
          {notification.related_post?.content.slice(0, 30)}{notification.related_post?.content.length > 30 ? '...' : ''}
        </span>
      </>);
    case 'follow':
      return (<>
        <Link to={`/@/${notification.events[0].actor.username}`} onClick={event => event.stopPropagation()}>
          {notification.events[0].actor.displayed_name} (@{notification.events[0].actor.username})
        </Link> zaczął(a) Cię obserwować 
      </>);
    case 'mention':
      return (<>
        <Link to={`/@/${notification.events[0].actor.username}`} onClick={event => event.stopPropagation()}>
          {notification.events[0].actor.displayed_name} (@{notification.events[0].actor.username})
        </Link> wspomniał(a) Cię w poście: <span className="fst-italic">
          {notification.related_post?.content.slice(0, 30)}{notification.related_post?.content.length > 30 ? '...' : ''}
        </span>
      </>);
    case 'followed_user_posted':
      return (<>
        <Link to={`/@/${notification.events[0].actor.username}`} onClick={event => event.stopPropagation()}>
          {notification.events[0].actor.displayed_name} (@{notification.events[0].actor.username})
        </Link> opublikował(a) nowy post: <span className="fst-italic">
          {notification.related_post?.content.slice(0, 30)}{notification.related_post?.content.length > 30 ? '...' : ''}
        </span>
      </>);
  }
}

function Notifications() {
  const [notifications, setNotifications] = useState(null);
  const [loading, setLoading] = useState(true);

  const { connectWebSocket } = useAuth();

  const navigate = useNavigate();

  const mergeNotifications = (notifications, newNotification) => {
    const exists = notifications.find(n => n.id === newNotification.id);

    if (exists) {
      return notifications.map(n => n.id === newNotification.id ? newNotification : n);
    }
    else {
      return [newNotification, ...notifications];
    }
  };

  const handleNotificationClick = notificationData => {
    const getPath = () => {
      if (['reply', 'like', 'mention', 'followed_user_posted'].includes(notificationData.notification_type)) {
        return `/post/${notificationData.related_post.id}`;
      }
      else if (notificationData.notification_type === 'follow') {
        return `/@/${notificationData.events[0].actor.username}`;
      }
    };

    markNotificationAsSeen(notificationData.id)
      .then(() => {
        setNotifications(prev => prev.map(notification => {
          if (notification.id === notificationData.id) {
            return {
              ...notification,
              events: notification.events.map(event => ({
                ...event,
                seen: true
              }))
            };
          }
          else return notification;
        }))
      })
      .catch(error => console.error(error));
    
    navigate(getPath());
  };

  const handleMarkAllNotifictionsAsSeen = () => {
    markAllNotificationsAsSeen()
      .then(() => {
        setNotifications(prev => prev.map(notification => {
            return {
              ...notification,
              events: notification.events.map(event => ({
                ...event,
                seen: true
              }))
            };
          }
        ));
      })
      .catch(error => console.error(error));
  };

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

  const getUnseenCount = notifications => {
    try {
      return notifications.filter(notification => notification.events.some(event => !event.seen)).length;
    }
    catch {
      return 0;
    }
  };

  return (<>
    <div className="dropdown">
      <button className="btn btn-primary" type="button" data-bs-toggle="dropdown">
        <i className="bi bi-bell-fill"></i>
          {notifications && getUnseenCount(notifications) > 0 && <>
            <span className="position-absolute top-0 start-100 translate-middle badge p-1 rounded-pill bg-danger">
              {getUnseenCount(notifications)}
              <span className="visually-hidden">powiadomienia</span>
            </span>
          </>}
      </button>
      <ul className="dropdown-menu dropdown-menu-end">
        {loading ? (<>
          <li className="dropdown-item">
            <div className="text-center dropdown-item-text">
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Ładowanie...</span>
              </div>      
            </div>
          </li>
        </>) : notifications ? notifications.map(notification => (<>
          <li
            className={`dropdown-item${notification.events.some(event => !event.seen) ? ' bg-info-subtle' : ''}`}
            key={notification.id}
          >
            <span className="dropdown-item-text" onClick={() => handleNotificationClick(notification)} role="button">
              <Notification notification={notification} />
            </span>
          </li>
        </>)) : (<>
          <li className="dropdown-item">
            <span className="dropdown-item-text">Brak nowych powiadomień</span>
          </li>
        </>)}
        {notifications && getUnseenCount(notifications) > 0 && (<>
          <li><hr className="dropdown-divider" /></li>
          <li className="dropdown-item" onClick={handleMarkAllNotifictionsAsSeen} role="button">
            Oznacz wszystkie jako przeczytane
          </li>
        </>)}
      </ul>
    </div>
  </>);
}

export default Notifications;