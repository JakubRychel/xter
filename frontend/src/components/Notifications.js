import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getNotifications, markNotificationAsSeen } from '../services/notifications';

function Notification({ notification }) {
  return (<>
    <li><span className="dropdown-item-text">{notification.notification_type}</span></li>
  </>);
}

function Notifications() {
  const [notifications, setNotifications] = useState(null);
  const [loading, setLoading] = useState(true);

  const { connectWebSocket } = useAuth();

  useEffect(() => {
    const fetchNotifications = async () => {
      const notifications = await getNotifications();

      setNotifications(notifications);
      setLoading(false);
    };

    fetchNotifications();

    const ws = connectWebSocket('notifications');

    ws.onmessage = event => {
      const data = JSON.parse(event.data);

      console.log('Received notification:', data);
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
          <li>
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