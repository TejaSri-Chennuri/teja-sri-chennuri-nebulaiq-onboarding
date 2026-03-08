import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { notificationAPI } from '../../services/api';

export default function NotificationBell() {
  const [count, setCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await notificationAPI.unreadCount();
        setCount(res.data.unread_count || 0);
      } catch {
        // ignore
      }
    };
    fetch();
    const interval = setInterval(fetch, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <button
      onClick={() => navigate('/notifications')}
      style={styles.btn}
      title="Notifications"
    >
      🔔
      {count > 0 && (
        <span style={styles.badge}>{count > 99 ? '99+' : count}</span>
      )}
    </button>
  );
}

const styles = {
  btn: {
    position: 'relative',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: '1.25rem',
    padding: '0.375rem',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    transition: 'background 0.15s',
  },
  badge: {
    position: 'absolute',
    top: '0',
    right: '0',
    background: '#ef4444',
    color: 'white',
    fontSize: '0.625rem',
    fontWeight: '700',
    width: '16px',
    height: '16px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    lineHeight: 1,
  },
};
