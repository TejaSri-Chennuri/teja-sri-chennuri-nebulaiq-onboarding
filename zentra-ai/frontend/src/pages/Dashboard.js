import React, { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';
import { Link } from 'react-router-dom';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import useAuthStore from '../hooks/useAuthStore';

const CATEGORY_COLORS = {
  streaming: '#ef4444',
  music: '#8b5cf6',
  productivity: '#3b82f6',
  cloud_storage: '#0ea5e9',
  fitness: '#10b981',
  gaming: '#f59e0b',
  food: '#f97316',
  education: '#14b8a6',
  communication: '#6366f1',
  security: '#64748b',
  other: '#94a3b8',
};

const PRIORITY_COLORS = { high: '#ef4444', medium: '#f59e0b', low: '#10b981' };

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsAPI.dashboard()
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={styles.loadingCenter}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
        <p style={{ marginTop: '1rem', color: 'var(--color-text-secondary)' }}>Loading dashboard...</p>
      </div>
    );
  }

  const summary = data?.summary || {};
  const categoryBreakdown = data?.category_breakdown || [];
  const monthlyTrend = data?.monthly_trend || [];
  const upcomingRenewals = data?.upcoming_renewals || [];
  const recommendations = data?.recommendations || [];
  const insights = data?.insights || [];

  const pieData = categoryBreakdown.map((c) => ({
    name: c.category,
    value: c.monthly_amount,
    color: CATEGORY_COLORS[c.category] || '#94a3b8',
  }));

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.pageHeader}>
        <div>
          <h1 style={styles.pageTitle}>Dashboard</h1>
          <p style={styles.pageSubtitle}>
            {user?.full_name ? `Welcome back, ${user.full_name.split(' ')[0]}!` : 'Your subscription overview'}
          </p>
        </div>
      </div>

      {/* AI Insights Banner */}
      {insights.length > 0 && (
        <div style={styles.insightBanner}>
          <span style={styles.insightIcon}>🤖</span>
          <span style={styles.insightText}>{insights[0]}</span>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
        <StatCard
          icon="💳"
          label="Monthly Spend"
          value={`₹${(summary.total_monthly_spend || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
          color="#6366f1"
        />
        <StatCard
          icon="📅"
          label="Annual Spend"
          value={`₹${(summary.total_annual_spend || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
          color="#8b5cf6"
        />
        <StatCard
          icon="✅"
          label="Active Subscriptions"
          value={summary.active_count || 0}
          color="#10b981"
        />
        <StatCard
          icon="⏰"
          label="Renewals (30 days)"
          value={upcomingRenewals.length}
          color="#f59e0b"
        />
      </div>

      {/* Charts Row */}
      <div style={styles.chartsRow}>
        {/* Spending Trend */}
        <div className="card" style={{ flex: 2 }}>
          <h3 style={styles.cardTitle}>Monthly Spending Trend</h3>
          {monthlyTrend.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={monthlyTrend}>
                <defs>
                  <linearGradient id="spendGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  formatter={(v) => [`₹${v.toLocaleString('en-IN')}`, 'Spend']}
                  contentStyle={{ borderRadius: '8px', fontSize: '0.875rem' }}
                />
                <Area
                  type="monotone"
                  dataKey="total_spend"
                  stroke="#6366f1"
                  strokeWidth={2}
                  fill="url(#spendGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState text="No spending data yet" />
          )}
        </div>

        {/* Category Pie */}
        <div className="card" style={{ flex: 1, minWidth: '260px' }}>
          <h3 style={styles.cardTitle}>By Category</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(v) => [`₹${v.toLocaleString('en-IN')}`, 'Spend']}
                  contentStyle={{ borderRadius: '8px', fontSize: '0.875rem' }}
                />
                <Legend
                  formatter={(v) => <span style={{ fontSize: '0.75rem' }}>{v}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState text="No subscriptions yet" />
          )}
        </div>
      </div>

      {/* Bottom Row */}
      <div style={styles.bottomRow}>
        {/* Upcoming Renewals */}
        <div className="card" style={{ flex: 1 }}>
          <div style={styles.cardHeader}>
            <h3 style={styles.cardTitle}>Upcoming Renewals</h3>
            <Link to="/subscriptions" style={styles.viewAll}>View all →</Link>
          </div>
          {upcomingRenewals.length > 0 ? (
            <div style={styles.renewalList}>
              {upcomingRenewals.slice(0, 5).map((r, i) => (
                <div key={i} style={styles.renewalItem}>
                  <div style={styles.renewalLeft}>
                    {r.logo_url ? (
                      <img src={r.logo_url} alt={r.name} style={styles.serviceLogo} />
                    ) : (
                      <div style={styles.serviceLogoPlaceholder}>📦</div>
                    )}
                    <div>
                      <div style={styles.serviceName}>{r.name}</div>
                      <div style={styles.serviceDate}>in {r.days_until_renewal} day{r.days_until_renewal !== 1 ? 's' : ''}</div>
                    </div>
                  </div>
                  <div style={styles.renewalAmount}>₹{r.amount.toLocaleString('en-IN')}</div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState text="No renewals in next 30 days" />
          )}
        </div>

        {/* Top Recommendations */}
        <div className="card" style={{ flex: 1 }}>
          <div style={styles.cardHeader}>
            <h3 style={styles.cardTitle}>AI Recommendations</h3>
            <Link to="/recommendations" style={styles.viewAll}>View all →</Link>
          </div>
          {recommendations.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {recommendations.slice(0, 3).map((rec, i) => (
                <div
                  key={i}
                  style={{
                    ...styles.recItem,
                    borderLeftColor: PRIORITY_COLORS[rec.priority] || '#94a3b8',
                  }}
                >
                  <div style={styles.recTitle}>{rec.title}</div>
                  {rec.potential_savings > 0 && (
                    <div style={styles.recSavings}>
                      Save ₹{rec.potential_savings.toLocaleString('en-IN', { maximumFractionDigits: 0 })}/mo
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <EmptyState text="No recommendations yet" />
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  return (
    <div className="stat-card">
      <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>{icon}</div>
      <div style={{ ...styles.statValue, color }}>{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function EmptyState({ text }) {
  return (
    <div style={styles.emptyState}>
      <span style={{ fontSize: '2rem', opacity: 0.3 }}>📭</span>
      <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>{text}</p>
    </div>
  );
}

const styles = {
  page: { display: 'flex', flexDirection: 'column', gap: '1.25rem' },
  loadingCenter: {
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    justifyContent: 'center', height: '60vh',
  },
  pageHeader: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
  },
  pageTitle: { fontSize: '1.75rem', fontWeight: '700', color: 'var(--color-text)' },
  pageSubtitle: { color: 'var(--color-text-secondary)', marginTop: '0.25rem', fontSize: '0.9rem' },
  insightBanner: {
    display: 'flex', alignItems: 'center', gap: '0.75rem',
    background: 'linear-gradient(135deg, #e0e7ff 0%, #ede9fe 100%)',
    border: '1px solid #c7d2fe',
    borderRadius: '10px', padding: '0.875rem 1.25rem',
  },
  insightIcon: { fontSize: '1.25rem' },
  insightText: { color: '#4338ca', fontSize: '0.9rem', fontWeight: '500' },
  chartsRow: { display: 'flex', gap: '1.25rem', flexWrap: 'wrap' },
  cardTitle: {
    fontSize: '1rem', fontWeight: '600', color: 'var(--color-text)',
    marginBottom: '1rem',
  },
  cardHeader: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    marginBottom: '1rem',
  },
  viewAll: {
    color: 'var(--color-primary)', fontSize: '0.8rem', textDecoration: 'none',
    fontWeight: '500',
  },
  statValue: { fontSize: '1.75rem', fontWeight: '700' },
  bottomRow: { display: 'flex', gap: '1.25rem', flexWrap: 'wrap' },
  renewalList: { display: 'flex', flexDirection: 'column', gap: '0.75rem' },
  renewalItem: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '0.625rem 0', borderBottom: '1px solid var(--color-border)',
  },
  renewalLeft: { display: 'flex', alignItems: 'center', gap: '0.75rem' },
  serviceLogo: { width: '32px', height: '32px', borderRadius: '8px', objectFit: 'contain' },
  serviceLogoPlaceholder: {
    width: '32px', height: '32px', borderRadius: '8px',
    background: 'var(--color-bg)', display: 'flex', alignItems: 'center',
    justifyContent: 'center', fontSize: '1rem',
  },
  serviceName: { fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-text)' },
  serviceDate: { fontSize: '0.75rem', color: 'var(--color-text-secondary)' },
  renewalAmount: { fontSize: '0.9rem', fontWeight: '600', color: 'var(--color-primary)' },
  recItem: {
    padding: '0.75rem',
    borderLeft: '3px solid',
    background: 'var(--color-bg)',
    borderRadius: '0 8px 8px 0',
  },
  recTitle: { fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-text)' },
  recSavings: {
    fontSize: '0.75rem', color: '#10b981', fontWeight: '500', marginTop: '0.25rem',
  },
  emptyState: {
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    justifyContent: 'center', padding: '2rem',
  },
};
