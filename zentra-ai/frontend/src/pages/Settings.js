import React, { useState, useEffect } from 'react';
import { authAPI, notificationAPI } from '../services/api';
import useAuthStore from '../hooks/useAuthStore';
import toast from 'react-hot-toast';

export default function Settings() {
  const { user, updateUser } = useAuthStore();
  const [profile, setProfile] = useState({
    full_name: user?.full_name || '',
    phone_number: user?.phone_number || '',
    currency: user?.currency || 'INR',
  });
  const [prefs, setPrefs] = useState(null);
  const [saving, setSaving] = useState(false);
  const [savingPrefs, setSavingPrefs] = useState(false);

  useEffect(() => {
    notificationAPI.getPreferences().then((res) => setPrefs(res.data)).catch(() => {});
  }, []);

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await authAPI.updateProfile(profile);
      updateUser(res.data);
      toast.success('Profile updated!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleSavePrefs = async (e) => {
    e.preventDefault();
    setSavingPrefs(true);
    try {
      const res = await notificationAPI.updatePreferences(prefs);
      setPrefs(res.data);
      toast.success('Notification preferences saved!');
    } catch {
      toast.error('Failed to save preferences');
    } finally {
      setSavingPrefs(false);
    }
  };

  const handleConnectGmail = async () => {
    try {
      const res = await authAPI.gmailAuthorize();
      if (res.data.auth_url) {
        window.location.href = res.data.auth_url;
      } else {
        toast.success(res.data.message || 'Gmail integration configured');
      }
    } catch {
      toast.error('Failed to connect Gmail');
    }
  };

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>Settings</h1>
      <p style={styles.subtitle}>Manage your account and preferences</p>

      <div style={styles.grid}>
        {/* Profile */}
        <div className="card">
          <h3 style={styles.cardTitle}>👤 Profile</h3>
          <form onSubmit={handleSaveProfile} style={styles.form}>
            <div>
              <label className="label">Full Name</label>
              <input
                className="input"
                value={profile.full_name}
                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="label">Email</label>
              <input className="input" value={user?.email || ''} disabled style={{ opacity: 0.7 }} />
            </div>
            <div>
              <label className="label">Phone Number</label>
              <input
                className="input"
                type="tel"
                placeholder="+91 9876543210"
                value={profile.phone_number}
                onChange={(e) => setProfile({ ...profile, phone_number: e.target.value })}
              />
            </div>
            <div>
              <label className="label">Currency</label>
              <select
                className="input"
                value={profile.currency}
                onChange={(e) => setProfile({ ...profile, currency: e.target.value })}
              >
                <option value="INR">INR (₹) - Indian Rupee</option>
                <option value="USD">USD ($) - US Dollar</option>
                <option value="EUR">EUR (€) - Euro</option>
                <option value="GBP">GBP (£) - British Pound</option>
              </select>
            </div>
            <button type="submit" className="btn btn-md btn-primary" disabled={saving}>
              {saving ? '⏳ Saving...' : '💾 Save Profile'}
            </button>
          </form>
        </div>

        {/* Integrations */}
        <div className="card">
          <h3 style={styles.cardTitle}>🔗 Integrations</h3>
          <div style={styles.integrations}>
            <IntegrationItem
              icon="📧"
              name="Gmail"
              description="Scan emails for subscriptions"
              connected={!!user?.gmail_access_token}
              onConnect={handleConnectGmail}
            />
            <IntegrationItem
              icon="🏦"
              name="Bank Accounts"
              description="Track transactions via Plaid"
              connected={!!user?.plaid_access_token}
              onConnect={() => toast.info('Plaid integration requires configuration')}
            />
            <IntegrationItem
              icon="📱"
              name="SMS"
              description="Detect payment alerts via SMS"
              connected={false}
              onConnect={() => toast.info('SMS integration coming soon')}
            />
          </div>
        </div>

        {/* Notification Preferences */}
        {prefs && (
          <div className="card" style={{ gridColumn: '1 / -1' }}>
            <h3 style={styles.cardTitle}>🔔 Notification Preferences</h3>
            <form onSubmit={handleSavePrefs}>
              <div style={styles.prefsGrid}>
                <div>
                  <h4 style={styles.prefsSubtitle}>Channels</h4>
                  <div style={styles.toggleList}>
                    {[
                      { key: 'email_enabled', label: '📧 Email notifications' },
                      { key: 'sms_enabled', label: '💬 SMS notifications' },
                      { key: 'push_enabled', label: '📱 Push notifications' },
                      { key: 'whatsapp_enabled', label: '💚 WhatsApp notifications' },
                      { key: 'voice_enabled', label: '🔊 Voice call alerts' },
                    ].map(({ key, label }) => (
                      <Toggle
                        key={key}
                        label={label}
                        checked={prefs[key]}
                        onChange={(v) => setPrefs({ ...prefs, [key]: v })}
                      />
                    ))}
                  </div>
                </div>
                <div>
                  <h4 style={styles.prefsSubtitle}>Alert Types</h4>
                  <div style={styles.toggleList}>
                    {[
                      { key: 'renewal_reminders', label: '⏰ Renewal reminders' },
                      { key: 'payment_alerts', label: '💳 Payment alerts' },
                      { key: 'unused_service_alerts', label: '💤 Unused service alerts' },
                      { key: 'spending_alerts', label: '💰 Spending alerts' },
                      { key: 'recommendation_alerts', label: '💡 AI recommendation alerts' },
                    ].map(({ key, label }) => (
                      <Toggle
                        key={key}
                        label={label}
                        checked={prefs[key]}
                        onChange={(v) => setPrefs({ ...prefs, [key]: v })}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <button type="submit" className="btn btn-md btn-primary" disabled={savingPrefs} style={{ marginTop: '1.5rem' }}>
                {savingPrefs ? '⏳ Saving...' : '💾 Save Preferences'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

function IntegrationItem({ icon, name, description, connected, onConnect }) {
  return (
    <div style={styles.integrationItem}>
      <span style={styles.integrationIcon}>{icon}</span>
      <div style={{ flex: 1 }}>
        <div style={styles.integrationName}>{name}</div>
        <div style={styles.integrationDesc}>{description}</div>
      </div>
      {connected ? (
        <span style={styles.connectedBadge}>✓ Connected</span>
      ) : (
        <button className="btn btn-sm btn-secondary" onClick={onConnect}>
          Connect
        </button>
      )}
    </div>
  );
}

function Toggle({ label, checked, onChange }) {
  return (
    <label style={styles.toggleItem}>
      <span style={styles.toggleLabel}>{label}</span>
      <div
        style={{
          ...styles.toggleSwitch,
          background: checked ? '#6366f1' : '#e2e8f0',
        }}
        onClick={() => onChange(!checked)}
      >
        <div
          style={{
            ...styles.toggleThumb,
            transform: checked ? 'translateX(20px)' : 'translateX(2px)',
          }}
        />
      </div>
    </label>
  );
}

const styles = {
  page: { display: 'flex', flexDirection: 'column', gap: '1.25rem' },
  title: { fontSize: '1.75rem', fontWeight: '700' },
  subtitle: { color: 'var(--color-text-secondary)', fontSize: '0.9rem' },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
    gap: '1.25rem',
  },
  cardTitle: { fontSize: '1rem', fontWeight: '600', marginBottom: '1.25rem' },
  form: { display: 'flex', flexDirection: 'column', gap: '1rem' },
  integrations: { display: 'flex', flexDirection: 'column', gap: '1rem' },
  integrationItem: { display: 'flex', alignItems: 'center', gap: '0.875rem', padding: '0.875rem 0', borderBottom: '1px solid var(--color-border)' },
  integrationIcon: { fontSize: '1.5rem', width: '2rem', textAlign: 'center' },
  integrationName: { fontSize: '0.9rem', fontWeight: '600' },
  integrationDesc: { fontSize: '0.8rem', color: 'var(--color-text-secondary)' },
  connectedBadge: { fontSize: '0.8rem', color: '#10b981', fontWeight: '600', background: '#d1fae5', padding: '0.25rem 0.625rem', borderRadius: '999px' },
  prefsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '2rem' },
  prefsSubtitle: { fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-text-secondary)', marginBottom: '0.75rem' },
  toggleList: { display: 'flex', flexDirection: 'column', gap: '0.75rem' },
  toggleItem: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' },
  toggleLabel: { fontSize: '0.875rem', color: 'var(--color-text)' },
  toggleSwitch: {
    width: '42px', height: '24px', borderRadius: '12px',
    position: 'relative', cursor: 'pointer', transition: 'background 0.2s',
    flexShrink: 0,
  },
  toggleThumb: {
    position: 'absolute', top: '2px', width: '20px', height: '20px',
    borderRadius: '50%', background: 'white',
    boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
    transition: 'transform 0.2s',
  },
};
