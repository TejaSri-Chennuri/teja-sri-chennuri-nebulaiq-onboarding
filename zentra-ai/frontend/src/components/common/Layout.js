import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import useAuthStore from '../../hooks/useAuthStore';
import NotificationBell from './NotificationBell';

const navItems = [
  { to: '/dashboard', icon: '📊', label: 'Dashboard' },
  { to: '/subscriptions', icon: '📱', label: 'Subscriptions' },
  { to: '/analytics', icon: '📈', label: 'Analytics' },
  { to: '/recommendations', icon: '💡', label: 'Recommendations' },
  { to: '/notifications', icon: '🔔', label: 'Notifications' },
  { to: '/settings', icon: '⚙️', label: 'Settings' },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={styles.container}>
      {/* Sidebar */}
      <aside style={{ ...styles.sidebar, transform: sidebarOpen ? 'translateX(0)' : undefined }}>
        {/* Logo */}
        <div style={styles.logo}>
          <span style={styles.logoIcon}>⚡</span>
          <span style={styles.logoText}>Zentra AI</span>
        </div>

        {/* Navigation */}
        <nav style={styles.nav}>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              style={({ isActive }) => ({
                ...styles.navItem,
                ...(isActive ? styles.navItemActive : {}),
              })}
              onClick={() => setSidebarOpen(false)}
            >
              <span style={styles.navIcon}>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* User */}
        <div style={styles.userSection}>
          <div style={styles.avatar}>
            {user?.full_name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div style={styles.userInfo}>
            <div style={styles.userName}>{user?.full_name}</div>
            <div style={styles.userEmail}>{user?.email}</div>
          </div>
          <button onClick={handleLogout} style={styles.logoutBtn} title="Logout">
            🚪
          </button>
        </div>
      </aside>

      {/* Main */}
      <main style={styles.main}>
        {/* Top bar */}
        <header style={styles.header}>
          <button
            style={styles.menuBtn}
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <div style={{ flex: 1 }} />
          <NotificationBell />
          <div style={styles.headerUser}>
            Hi, {user?.full_name?.split(' ')[0]} 👋
          </div>
        </header>

        {/* Page Content */}
        <div style={styles.content}>
          <Outlet />
        </div>
      </main>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          style={styles.overlay}
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    height: '100vh',
    overflow: 'hidden',
  },
  sidebar: {
    width: '260px',
    flexShrink: 0,
    background: '#1e1b4b',
    display: 'flex',
    flexDirection: 'column',
    padding: '1.5rem 1rem',
    gap: '0.5rem',
    overflowY: 'auto',
    zIndex: 100,
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.5rem 0.75rem',
    marginBottom: '1.5rem',
  },
  logoIcon: {
    fontSize: '1.75rem',
  },
  logoText: {
    fontSize: '1.25rem',
    fontWeight: '700',
    color: 'white',
    letterSpacing: '-0.025em',
  },
  nav: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem',
    flex: 1,
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.625rem 0.875rem',
    borderRadius: '10px',
    color: 'rgba(255,255,255,0.65)',
    textDecoration: 'none',
    fontSize: '0.9rem',
    fontWeight: '500',
    transition: 'all 0.15s',
  },
  navItemActive: {
    background: 'rgba(99,102,241,0.3)',
    color: 'white',
  },
  navIcon: {
    fontSize: '1.1rem',
    width: '1.5rem',
    textAlign: 'center',
  },
  userSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.75rem',
    borderTop: '1px solid rgba(255,255,255,0.1)',
    marginTop: 'auto',
  },
  avatar: {
    width: '36px',
    height: '36px',
    borderRadius: '50%',
    background: '#6366f1',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: '700',
    fontSize: '0.875rem',
    flexShrink: 0,
  },
  userInfo: {
    flex: 1,
    overflow: 'hidden',
  },
  userName: {
    color: 'white',
    fontSize: '0.875rem',
    fontWeight: '600',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  userEmail: {
    color: 'rgba(255,255,255,0.5)',
    fontSize: '0.75rem',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  logoutBtn: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: '1.1rem',
    padding: '0.25rem',
    borderRadius: '6px',
    opacity: 0.7,
  },
  main: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    background: 'var(--color-bg)',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    padding: '0.875rem 1.5rem',
    background: 'white',
    borderBottom: '1px solid var(--color-border)',
    height: '60px',
  },
  menuBtn: {
    display: 'none',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: '1.25rem',
    color: 'var(--color-text)',
    '@media (max-width: 768px)': { display: 'block' },
  },
  headerUser: {
    fontSize: '0.875rem',
    color: 'var(--color-text-secondary)',
    fontWeight: '500',
  },
  content: {
    flex: 1,
    overflowY: 'auto',
    padding: '1.5rem',
  },
  overlay: {
    display: 'none',
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.5)',
    zIndex: 99,
    '@media (max-width: 768px)': { display: 'block' },
  },
};
