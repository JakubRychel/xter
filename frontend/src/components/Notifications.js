import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { timeAgo } from '../utils/time';
import { useNavigate, Link } from 'react-router';
import { getNotifications, markNotificationAsSeen, markAllNotificationsAsSeen } from '../services/notifications';

function Notification({ notification }) {
  switch (notification.notification_type) {
    case 'reply':
      return (<>
        <Link
          to={`/@/${notification.latest_actors[0].username}`}
          onClick={event => event.stopPropagation()}
          className="text-dark fw-bold text-decoration-none"
        >
          {notification.latest_actors[0].displayed_name} (@{notification.latest_actors[0].username})
        </Link> odpowiedział(a) na Twój post: <span className="fst-italic">
          {notification.related_post?.content.slice(0, 30)}{notification.related_post?.content.length > 30 ? '...' : ''}
        </span>
      </>);
    case 'like':
      return (<>
        {notification.latest_actors.map((actor, index) => (
          <React.Fragment key={actor.id}>
            <Link
              to={`/@/${actor.username}`}
              onClick={event => event.stopPropagation()}
              className="text-dark fw-bold text-decoration-none"
            >
              {actor.displayed_name} (@{actor.username})
            </Link>
            {index === notification.events_count - 2 && ' i '} 
            {index < notification.events_count - 2 && ', '}
          </React.Fragment>
        ))}
        {notification.events_count > notification.latest_actors.length
          && `${notification.events_count - notification.latest_actors.length} innych`
        }
        {notification.events_count <= 1 ? ' polubił(a) Twój post: ' : ' polubili/ły Twój post: '}
        <span className="fst-italic">
          {notification.related_post?.content.slice(0, 30)}{notification.related_post?.content.length > 30 ? '...' : ''}
        </span>
      </>);
    case 'follow':
      return (<>
        {notification.latest_actors.map((actor, index) => (
          <React.Fragment key={actor.id}>
            <Link
              to={`/@/${actor.username}`}
              onClick={event => event.stopPropagation()}
              className="text-dark fw-bold text-decoration-none"
            >
              {actor.displayed_name} (@{actor.username})
            </Link>
            {index === notification.events_count - 2 && ' i '} 
            {index < notification.events_count - 2 && ', '}
          </React.Fragment>
        ))}
        {notification.events_count > notification.latest_actors.length
          && `${notification.events_count - notification.latest_actors.length} innych`
        }
        {notification.events_count <= 1 ? ' zaczął/ęła Cię obserwować' : ' zaczęli Cię obserwować'}
      </>);
    case 'mention':
      return (<>
        <Link
          to={`/@/${notification.latest_actors[0].username}`}
          onClick={event => event.stopPropagation()}
          className="text-dark fw-bold text-decoration-none"
        >
          {notification.latest_actors[0].displayed_name} (@{notification.latest_actors[0].username})
        </Link> wspomniał(a) Cię w poście: <span className="fst-italic">
          {notification.related_post?.content.slice(0, 30)}{notification.related_post?.content.length > 30 ? '...' : ''}
        </span>
      </>);
    case 'followed_user_posted':
      return (<>
        <Link
          to={`/@/${notification.latest_actors[0].username}`}
          onClick={event => event.stopPropagation()}
          className="text-dark fw-bold text-decoration-none"
        >
          {notification.latest_actors[0].displayed_name} (@{notification.latest_actors[0].username})
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
    const filtered = notifications.filter(n => n.id !== newNotification.id);

    return [newNotification, ...filtered];
  };

  const handleNotificationClick = notificationData => {
    markNotificationAsSeen(notificationData.id)
      .then(() => {
        setNotifications(prev => prev.map(notification => {
          if (notification.id === notificationData.id) {
            return {
              ...notification,
              seen: true
            };
          }
          else return notification;
        }))
      })
      .catch(error => console.error(error));
    
    if (['reply', 'like', 'mention', 'followed_user_posted'].includes(notificationData.notification_type)) {
      navigate(`/post/${notificationData.related_post.id}`);
    }
  };

  const handleMarkAllNotifictionsAsSeen = () => {
    markAllNotificationsAsSeen()
      .then(() => {
        setNotifications(prev => prev.map(notification => {
            return {
              ...notification,
              seen: true
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
      return notifications.filter(notification => !notification.seen).length;
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
        <li>
          <span className="dropdown-item-text d-flex align-items-baseline py-2">

            <h6 className="dopdown-header fw-bold mb-0">Powiadomienia</h6>

            {notifications && getUnseenCount(notifications) > 0 && (<>
              <button className="btn btn-link text-decoration-none p-0 mb-0 ms-auto" onClick={handleMarkAllNotifictionsAsSeen}>
                <i className="bi bi-check-all"></i> Oznacz wszystkie jako przeczytane
              </button>
            </>)}

          </span>
        </li>
        {loading ? (<>
          <li>
            <div className="dropdown-item-text py-2 border-top text-center">
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Ładowanie...</span>
              </div>      
            </div>
          </li>
        </>) : notifications.length > 0 ? notifications.map(notification => (
          <li key={notification.id}>
            <span 
              className={`dropdown-item py-2 border-top${!notification.seen ? ' bg-light' : ''}`}
              onClick={() => handleNotificationClick(notification)} role="button"
            >
              <Notification notification={notification} />

              <div>
                <small className="text-muted">{timeAgo(notification.updated_at)}</small>
              </div>
            </span>
          </li>
        )) : (<>
          <li>
            <span className="dropdown-item-text py-2 border-top text-center">
              Brak powiadomień
            </span>
          </li>
        </>)}
      </ul>
    </div>
  </>);
}

export default Notifications;