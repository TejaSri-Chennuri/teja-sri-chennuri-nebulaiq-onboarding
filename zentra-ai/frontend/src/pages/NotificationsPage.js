import React, { useState, useEffect } from 'react';
import { notificationAPI } from '../services/api';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

const TYPE_ICONS = {
  renewal_reminder: '⏰',
  payment_detected: '💳',
  unused_service: '💤',
  price_increase: '📈',
  recommendation: '💡',
  spending_alert: '💰',
  duplicate_detected: '🔁',
  trial_ending: '⌛',
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchNotifications = async () => {
    try {
      const res = await notificationAPI.list({ unread_only: unreadOnly });
      setNotifications(res.data);
      const countRes = await notificationAPI.unreadCount();
      setUnreadCount(countRes.data.unread_count);
    } catch {
      toast.error('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchNotifications(); }, [unreadOnly]);

  const handleMarkRead = async (id) => {
    try {
      await notificationAPI.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => n.id === id ? { ...n, is_read: true } : n)
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch {
      toast.error('Failed to mark as read');
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationAPI.markAllRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
      toast.success('All notifications marked as read');
    } catch {
      toast.error('Failed to mark all as read');
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Notifications</h1>
          <p style={styles.subtitle}>
            {unreadCount > 0 ? `${unreadCount} unread` : 'All caught up!'}
          </p>
        </div>
        <div style={styles.actions}>
          <button
            className={`btn btn-sm ${unreadOnly ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setUnreadOnly(!unreadOnly)}
          >
            {unreadOnly ? '🔴 Unread only' : '📋 All'}
          </button>
          {unreadCount > 0 && (
            <button className="btn btn-sm btn-ghost" onClick={handleMarkAllRead}>
              ✓ Mark all read
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <div className="spinner" />
        </div>
      ) : notifications.length === 0 ? (
        <div className="card" style={styles.emptyCard}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔔</div>
          <h3 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>No notifications</h3>
          <p style={{ color: 'var(--color-text-secondary)' }}>
            {unreadOnly ? 'No unread notifications' : "You're all caught up!"}
          </p>
        </div>
      ) : (
        <div style={styles.notifList}>
          {notifications.map((notif) => (
            <NotificationItem
              key={notif.id}
              notif={notif}
              onMarkRead={() => handleMarkRead(notif.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function NotificationItem({ notif, onMarkRead }) {
  const icon = TYPE_ICONS[notif.notification_type] || '🔔';
  const timeAgo = notif.created_at
    ? format(new Date(notif.created_at), 'MMM d, h:mm a')
    : '';

  return (
    <div
      className="card"
      style={{
        ...styles.notifCard,
        background: notif.is_read ? 'white' : '#f0f4ff',
        borderLeft: `4px solid ${notif.is_read ? 'var(--color-border)' : 'var(--color-primary)'}`,
      }}
    >
      <div style={styles.notifTop}>
        <span style={styles.notifIcon}>{icon}</span>
        <div style={{ flex: 1 }}>
          <div style={styles.notifTitle}>{notif.title}</div>
          <div style={styles.notifMessage}>{notif.message}</div>
        </div>
        <div style={styles.notifRight}>
          <span style={styles.notifTime}>{timeAgo}</span>
          {!notif.is_read && (
            <button className="btn btn-sm btn-ghost" onClick={onMarkRead} style={{ fontSize: '0.75rem' }}>
              Mark read
            </button>
          )}
        </div>
      </div>
      <div style={styles.notifMeta}>
        <span style={styles.channelTag}>{notif.channel}</span>
        <span style={styles.typeTag}>{notif.notification_type?.replace('_', ' ')}</span>
        {!notif.is_read && <span style={styles.unreadDot} />}
      </div>
    </div>
  );
}

const styles = {
  page: { display: 'flex', flexDirection: 'column', gap: '1.25rem' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' },
  title: { fontSize: '1.75rem', fontWeight: '700' },
  subtitle: { color: 'var(--color-text-secondary)', fontSize: '0.9rem' },
  actions: { display: 'flex', gap: '0.75rem' },
  emptyCard: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '3rem', textAlign: 'center' },
  notifList: { display: 'flex', flexDirection: 'column', gap: '0.75rem' },
  notifCard: { display: 'flex', flexDirection: 'column', gap: '0.625rem' },
  notifTop: { display: 'flex', alignItems: 'flex-start', gap: '0.875rem' },
  notifIcon: { fontSize: '1.5rem', flexShrink: 0, marginTop: '0.125rem' },
  notifTitle: { fontSize: '0.9rem', fontWeight: '600', color: 'var(--color-text)', marginBottom: '0.25rem' },
  notifMessage: { fontSize: '0.875rem', color: 'var(--color-text-secondary)', lineHeight: 1.5 },
  notifRight: { display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.375rem', flexShrink: 0 },
  notifTime: { fontSize: '0.75rem', color: 'var(--color-text-muted)', whiteSpace: 'nowrap' },
  notifMeta: { display: 'flex', alignItems: 'center', gap: '0.5rem' },
  channelTag: {
    padding: '0.125rem 0.5rem', borderRadius: '999px', fontSize: '0.7rem',
    background: '#e0e7ff', color: '#4338ca', fontWeight: '500',
  },
  typeTag: {
    padding: '0.125rem 0.5rem', borderRadius: '999px', fontSize: '0.7rem',
    background: 'var(--color-bg)', color: 'var(--color-text-secondary)',
  },
  unreadDot: {
    width: '8px', height: '8px', borderRadius: '50%', background: '#6366f1',
    marginLeft: 'auto',
  },
};
