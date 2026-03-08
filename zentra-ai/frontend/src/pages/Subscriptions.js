import React, { useState, useEffect } from 'react';
import { subscriptionAPI } from '../services/api';
import toast from 'react-hot-toast';

const STATUS_LABELS = {
  active: { label: 'Active', class: 'badge-active' },
  paused: { label: 'Paused', class: 'badge-paused' },
  cancelled: { label: 'Cancelled', class: 'badge-cancelled' },
  trial: { label: 'Trial', class: 'badge-trial' },
  expired: { label: 'Expired', class: 'badge-cancelled' },
};

const CATEGORIES = [
  'all', 'streaming', 'music', 'productivity', 'cloud_storage',
  'fitness', 'gaming', 'food', 'education', 'communication', 'security', 'other',
];

const BILLING_CYCLES = ['monthly', 'annual', 'quarterly', 'weekly', 'daily'];

export default function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('active');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [showAdd, setShowAdd] = useState(false);
  const [scanning, setScanning] = useState(false);

  const fetchSubs = async () => {
    try {
      const params = {};
      if (filter !== 'all') params.status_filter = filter;
      if (categoryFilter !== 'all') params.category = categoryFilter;
      const res = await subscriptionAPI.list(params);
      setSubscriptions(res.data);
    } catch (err) {
      toast.error('Failed to load subscriptions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchSubs(); }, [filter, categoryFilter]);

  const handleCancel = async (id, name) => {
    if (!window.confirm(`Cancel ${name}?`)) return;
    try {
      await subscriptionAPI.cancel(id);
      toast.success(`${name} cancelled`);
      fetchSubs();
    } catch {
      toast.error('Failed to cancel');
    }
  };

  const handleScanGmail = async () => {
    setScanning(true);
    try {
      const res = await subscriptionAPI.scanGmail();
      toast.success(res.data.message);
      fetchSubs();
    } catch {
      toast.error('Gmail scan failed');
    } finally {
      setScanning(false);
    }
  };

  const handleScanBank = async () => {
    setScanning(true);
    try {
      const res = await subscriptionAPI.scanBank();
      toast.success(res.data.message);
      fetchSubs();
    } catch {
      toast.error('Bank scan failed');
    } finally {
      setScanning(false);
    }
  };

  const totalMonthly = subscriptions
    .filter((s) => s.status === 'active')
    .reduce((sum, s) => {
      const monthly = s.billing_cycle === 'annual'
        ? s.amount / 12
        : s.billing_cycle === 'quarterly'
        ? s.amount / 3
        : s.amount;
      return sum + monthly;
    }, 0);

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Subscriptions</h1>
          <p style={styles.subtitle}>
            {subscriptions.filter((s) => s.status === 'active').length} active ·{' '}
            ₹{totalMonthly.toLocaleString('en-IN', { maximumFractionDigits: 0 })}/month
          </p>
        </div>
        <div style={styles.actions}>
          <button
            className="btn btn-md btn-secondary"
            onClick={handleScanGmail}
            disabled={scanning}
          >
            {scanning ? '⏳' : '📧'} Scan Gmail
          </button>
          <button
            className="btn btn-md btn-secondary"
            onClick={handleScanBank}
            disabled={scanning}
          >
            {scanning ? '⏳' : '🏦'} Scan Bank
          </button>
          <button
            className="btn btn-md btn-primary"
            onClick={() => setShowAdd(true)}
          >
            + Add Subscription
          </button>
        </div>
      </div>

      {/* Filters */}
      <div style={styles.filters}>
        <div style={styles.filterGroup}>
          {['all', 'active', 'paused', 'cancelled', 'trial'].map((s) => (
            <button
              key={s}
              className={`btn btn-sm ${filter === s ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setFilter(s)}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
        <select
          className="input"
          style={{ maxWidth: '160px' }}
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c.charAt(0).toUpperCase() + c.replace('_', ' ').slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* List */}
      {loading ? (
        <div style={styles.loadingCenter}><div className="spinner" /></div>
      ) : subscriptions.length === 0 ? (
        <div className="card" style={styles.emptyCard}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📭</div>
          <h3 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>No subscriptions found</h3>
          <p style={{ color: 'var(--color-text-secondary)', marginBottom: '1.5rem' }}>
            Add manually or scan your Gmail/bank for subscriptions
          </p>
          <button className="btn btn-md btn-primary" onClick={() => setShowAdd(true)}>
            + Add Subscription
          </button>
        </div>
      ) : (
        <div style={styles.grid}>
          {subscriptions.map((sub) => (
            <SubscriptionCard
              key={sub.id}
              sub={sub}
              onCancel={() => handleCancel(sub.id, sub.name)}
              onRefresh={fetchSubs}
            />
          ))}
        </div>
      )}

      {/* Add Modal */}
      {showAdd && (
        <AddSubscriptionModal
          onClose={() => setShowAdd(false)}
          onSuccess={() => { setShowAdd(false); fetchSubs(); }}
        />
      )}
    </div>
  );
}

function SubscriptionCard({ sub, onCancel, onRefresh }) {
  const statusInfo = STATUS_LABELS[sub.status] || { label: sub.status, class: 'badge-active' };
  const monthly = sub.billing_cycle === 'annual'
    ? sub.amount / 12
    : sub.billing_cycle === 'quarterly'
    ? sub.amount / 3
    : sub.amount;

  return (
    <div className="card card-hover" style={styles.subCard}>
      <div style={styles.subCardTop}>
        <div style={styles.subLogoWrap}>
          {sub.logo_url ? (
            <img src={sub.logo_url} alt={sub.name} style={styles.subLogo} />
          ) : (
            <div style={styles.subLogoPlaceholder}>{sub.name[0]}</div>
          )}
        </div>
        <div style={{ flex: 1 }}>
          <div style={styles.subName}>{sub.name}</div>
          <div style={styles.subMerchant}>{sub.category}</div>
        </div>
        <span className={`badge ${statusInfo.class}`}>{statusInfo.label}</span>
      </div>

      <div style={styles.subAmount}>
        <span style={styles.amountBig}>
          ₹{sub.amount.toLocaleString('en-IN')}
        </span>
        <span style={styles.amountCycle}>/{sub.billing_cycle}</span>
      </div>

      {sub.billing_cycle !== 'monthly' && (
        <div style={styles.monthlyEquiv}>
          ≈ ₹{monthly.toLocaleString('en-IN', { maximumFractionDigits: 0 })}/month
        </div>
      )}

      {sub.next_billing_date && (
        <div style={styles.nextDate}>
          🗓 Next: {new Date(sub.next_billing_date).toLocaleDateString('en-IN')}
        </div>
      )}

      {sub.usage_score < 20 && sub.status === 'active' && (
        <div style={styles.lowUsageAlert}>
          ⚠️ Low usage detected
        </div>
      )}

      <div style={styles.subActions}>
        {sub.ai_confidence < 1 && (
          <span style={styles.aiTag}>🤖 AI detected ({Math.round(sub.ai_confidence * 100)}%)</span>
        )}
        {sub.status === 'active' && (
          <button className="btn btn-sm btn-danger" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}

function AddSubscriptionModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({
    name: '', merchant: '', amount: '', currency: 'INR',
    billing_cycle: 'monthly', category: 'other',
    description: '', next_billing_date: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await subscriptionAPI.create({
        ...form,
        amount: parseFloat(form.amount),
        next_billing_date: form.next_billing_date || undefined,
      });
      toast.success(`${form.name} added!`);
      onSuccess();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add subscription');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.modalOverlay}>
      <div style={styles.modal}>
        <div style={styles.modalHeader}>
          <h2 style={styles.modalTitle}>Add Subscription</h2>
          <button className="btn btn-sm btn-ghost" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} style={styles.form}>
          <div className="grid-2">
            <div>
              <label className="label">Service Name *</label>
              <input
                className="input"
                placeholder="e.g. Netflix"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value, merchant: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="label">Amount (₹) *</label>
              <input
                className="input"
                type="number"
                placeholder="649"
                value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })}
                required
                min="0"
                step="0.01"
              />
            </div>
            <div>
              <label className="label">Billing Cycle</label>
              <select className="input" value={form.billing_cycle} onChange={(e) => setForm({ ...form, billing_cycle: e.target.value })}>
                {BILLING_CYCLES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Category</label>
              <select className="input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                {CATEGORIES.filter((c) => c !== 'all').map((c) => (
                  <option key={c} value={c}>{c.replace('_', ' ')}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Next Billing Date</label>
              <input
                className="input"
                type="date"
                value={form.next_billing_date}
                onChange={(e) => setForm({ ...form, next_billing_date: e.target.value })}
              />
            </div>
            <div>
              <label className="label">Currency</label>
              <select className="input" value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })}>
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
              </select>
            </div>
          </div>
          <div>
            <label className="label">Notes</label>
            <input
              className="input"
              placeholder="Optional notes"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
          <div style={styles.modalActions}>
            <button type="button" className="btn btn-md btn-ghost" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-md btn-primary" disabled={loading}>
              {loading ? '⏳ Adding...' : '+ Add Subscription'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const styles = {
  page: { display: 'flex', flexDirection: 'column', gap: '1.25rem' },
  header: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
    flexWrap: 'wrap', gap: '1rem',
  },
  title: { fontSize: '1.75rem', fontWeight: '700' },
  subtitle: { color: 'var(--color-text-secondary)', fontSize: '0.9rem' },
  actions: { display: 'flex', gap: '0.75rem', flexWrap: 'wrap' },
  filters: {
    display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap',
  },
  filterGroup: { display: 'flex', gap: '0.5rem', flexWrap: 'wrap' },
  loadingCenter: {
    display: 'flex', justifyContent: 'center', padding: '3rem',
  },
  emptyCard: {
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    justifyContent: 'center', padding: '3rem', textAlign: 'center',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1rem',
  },
  subCard: { display: 'flex', flexDirection: 'column', gap: '0.75rem' },
  subCardTop: { display: 'flex', alignItems: 'center', gap: '0.75rem' },
  subLogoWrap: { flexShrink: 0 },
  subLogo: { width: '40px', height: '40px', borderRadius: '10px', objectFit: 'contain' },
  subLogoPlaceholder: {
    width: '40px', height: '40px', borderRadius: '10px',
    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '1.25rem', fontWeight: '700',
  },
  subName: { fontSize: '1rem', fontWeight: '600', color: 'var(--color-text)' },
  subMerchant: { fontSize: '0.75rem', color: 'var(--color-text-secondary)', textTransform: 'capitalize' },
  subAmount: { display: 'flex', alignItems: 'baseline', gap: '0.25rem' },
  amountBig: { fontSize: '1.5rem', fontWeight: '700', color: 'var(--color-primary)' },
  amountCycle: { fontSize: '0.875rem', color: 'var(--color-text-secondary)' },
  monthlyEquiv: { fontSize: '0.8rem', color: 'var(--color-text-secondary)' },
  nextDate: { fontSize: '0.8rem', color: 'var(--color-text-secondary)' },
  lowUsageAlert: {
    fontSize: '0.75rem', color: '#92400e',
    background: '#fef3c7', padding: '0.375rem 0.625rem',
    borderRadius: '6px',
  },
  subActions: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'auto' },
  aiTag: { fontSize: '0.7rem', color: 'var(--color-text-muted)' },
  modalOverlay: {
    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    zIndex: 1000, padding: '1rem',
  },
  modal: {
    background: 'white', borderRadius: '16px', padding: '2rem',
    width: '100%', maxWidth: '560px', maxHeight: '90vh', overflowY: 'auto',
    boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
  },
  modalHeader: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    marginBottom: '1.5rem',
  },
  modalTitle: { fontSize: '1.25rem', fontWeight: '700' },
  form: { display: 'flex', flexDirection: 'column', gap: '1rem' },
  modalActions: {
    display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem',
  },
};
