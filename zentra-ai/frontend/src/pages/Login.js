import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../hooks/useAuthStore';
import toast from 'react-hot-toast';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, loading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(email, password);
    if (result.success) {
      toast.success('Welcome back! 👋');
      navigate('/dashboard');
    } else {
      toast.error(result.error || 'Login failed');
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        {/* Logo */}
        <div style={styles.logo}>
          <span style={styles.logoIcon}>⚡</span>
          <span style={styles.logoText}>Zentra AI</span>
        </div>
        <h2 style={styles.title}>Welcome back</h2>
        <p style={styles.subtitle}>Sign in to manage your subscriptions</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div>
            <label className="label">Email</label>
            <input
              className="input"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div>
            <label className="label">Password</label>
            <input
              className="input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="btn btn-lg btn-primary"
            disabled={loading}
            style={{ width: '100%' }}
          >
            {loading ? '⏳ Signing in...' : '→ Sign In'}
          </button>
        </form>

        <p style={styles.footer}>
          Don't have an account?{' '}
          <Link to="/register" style={styles.link}>Create one</Link>
        </p>
      </div>

      {/* Background decorations */}
      <div style={styles.bg1} />
      <div style={styles.bg2} />
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%)',
    padding: '1rem',
    position: 'relative',
    overflow: 'hidden',
  },
  card: {
    background: 'white',
    borderRadius: '20px',
    padding: '2.5rem',
    width: '100%',
    maxWidth: '420px',
    boxShadow: '0 25px 50px rgba(0,0,0,0.3)',
    position: 'relative',
    zIndex: 1,
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    marginBottom: '1.5rem',
    justifyContent: 'center',
  },
  logoIcon: { fontSize: '2rem' },
  logoText: {
    fontSize: '1.5rem', fontWeight: '700',
    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  title: { fontSize: '1.5rem', fontWeight: '700', textAlign: 'center', marginBottom: '0.375rem' },
  subtitle: { color: 'var(--color-text-secondary)', textAlign: 'center', marginBottom: '2rem', fontSize: '0.9rem' },
  form: { display: 'flex', flexDirection: 'column', gap: '1.125rem' },
  footer: { textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)' },
  link: { color: 'var(--color-primary)', fontWeight: '600', textDecoration: 'none' },
  bg1: {
    position: 'absolute', top: '-100px', right: '-100px',
    width: '300px', height: '300px', borderRadius: '50%',
    background: 'rgba(99,102,241,0.2)', filter: 'blur(40px)',
  },
  bg2: {
    position: 'absolute', bottom: '-100px', left: '-100px',
    width: '300px', height: '300px', borderRadius: '50%',
    background: 'rgba(139,92,246,0.2)', filter: 'blur(40px)',
  },
};
