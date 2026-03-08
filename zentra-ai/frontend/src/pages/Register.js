import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../hooks/useAuthStore';
import toast from 'react-hot-toast';

export default function Register() {
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    phone_number: '',
    currency: 'INR',
  });
  const { register: registerUser, loading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await registerUser(form);
    if (result.success) {
      toast.success('Account created! Welcome to Zentra AI 🎉');
      navigate('/dashboard');
    } else {
      toast.error(result.error || 'Registration failed');
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>
          <span style={styles.logoIcon}>⚡</span>
          <span style={styles.logoText}>Zentra AI</span>
        </div>
        <h2 style={styles.title}>Create your account</h2>
        <p style={styles.subtitle}>Start optimizing your subscriptions with AI</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div>
            <label className="label">Full Name *</label>
            <input
              className="input"
              placeholder="Your name"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              required
              autoFocus
            />
          </div>
          <div>
            <label className="label">Email *</label>
            <input
              className="input"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="label">Password *</label>
            <input
              className="input"
              type="password"
              placeholder="Minimum 8 characters"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              minLength={8}
            />
          </div>
          <div className="grid-2">
            <div>
              <label className="label">Phone (optional)</label>
              <input
                className="input"
                type="tel"
                placeholder="+91 9876543210"
                value={form.phone_number}
                onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
              />
            </div>
            <div>
              <label className="label">Currency</label>
              <select
                className="input"
                value={form.currency}
                onChange={(e) => setForm({ ...form, currency: e.target.value })}
              >
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            className="btn btn-lg btn-primary"
            disabled={loading}
            style={{ width: '100%', marginTop: '0.5rem' }}
          >
            {loading ? '⏳ Creating account...' : '🚀 Create Account'}
          </button>
        </form>

        <div style={styles.features}>
          {['🤖 AI subscription detection', '📊 Smart analytics', '💡 Cost optimization tips'].map((f) => (
            <span key={f} style={styles.feature}>{f}</span>
          ))}
        </div>

        <p style={styles.footer}>
          Already have an account?{' '}
          <Link to="/login" style={styles.link}>Sign in</Link>
        </p>
      </div>
      <div style={styles.bg1} />
      <div style={styles.bg2} />
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
    background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%)',
    padding: '1rem', position: 'relative', overflow: 'hidden',
  },
  card: {
    background: 'white', borderRadius: '20px', padding: '2.5rem',
    width: '100%', maxWidth: '460px',
    boxShadow: '0 25px 50px rgba(0,0,0,0.3)',
    position: 'relative', zIndex: 1,
  },
  logo: { display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem', justifyContent: 'center' },
  logoIcon: { fontSize: '2rem' },
  logoText: {
    fontSize: '1.5rem', fontWeight: '700',
    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
  },
  title: { fontSize: '1.4rem', fontWeight: '700', textAlign: 'center', marginBottom: '0.375rem' },
  subtitle: { color: 'var(--color-text-secondary)', textAlign: 'center', marginBottom: '1.5rem', fontSize: '0.9rem' },
  form: { display: 'flex', flexDirection: 'column', gap: '1rem' },
  features: { display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '1.25rem', justifyContent: 'center' },
  feature: {
    fontSize: '0.75rem', background: '#ede9fe', color: '#5b21b6',
    padding: '0.25rem 0.625rem', borderRadius: '999px', fontWeight: '500',
  },
  footer: { textAlign: 'center', marginTop: '1.25rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)' },
  link: { color: 'var(--color-primary)', fontWeight: '600', textDecoration: 'none' },
  bg1: { position: 'absolute', top: '-80px', right: '-80px', width: '250px', height: '250px', borderRadius: '50%', background: 'rgba(99,102,241,0.2)', filter: 'blur(40px)' },
  bg2: { position: 'absolute', bottom: '-80px', left: '-80px', width: '250px', height: '250px', borderRadius: '50%', background: 'rgba(139,92,246,0.2)', filter: 'blur(40px)' },
};
