import React, { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';
import toast from 'react-hot-toast';

const ACTION_ICONS = {
  cancel: '🗑️', pause: '⏸️', switch: '🔄',
  downgrade: '📉', review: '👀',
};

const PRIORITY_COLORS = { high: '#ef4444', medium: '#f59e0b', low: '#10b981' };
const PRIORITY_BG = { high: '#fee2e2', medium: '#fef3c7', low: '#d1fae5' };

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsAPI.recommendations(),
      analyticsAPI.insights(),
    ]).then(([r, i]) => {
      setRecommendations(r.data);
      setInsights(i.data);
    }).finally(() => setLoading(false));
  }, []);

  const totalSavings = recommendations.reduce((sum, r) => sum + (r.potential_savings || 0), 0);
  const highCount = recommendations.filter((r) => r.priority === 'high').length;

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}><div className="spinner" style={{ width: 40, height: 40 }} /></div>;
  }

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>AI Recommendations</h1>
      <p style={styles.subtitle}>Personalized suggestions to optimize your subscription spending</p>

      {/* Summary */}
      <div className="grid-3">
        <div className="stat-card">
          <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>💡</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '700', color: '#6366f1' }}>{recommendations.length}</div>
          <div className="stat-label">Total Recommendations</div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>🚨</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '700', color: '#ef4444' }}>{highCount}</div>
          <div className="stat-label">High Priority Actions</div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>💰</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '700', color: '#10b981' }}>
            ₹{totalSavings.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
          <div className="stat-label">Monthly Savings Potential</div>
        </div>
      </div>

      {/* Insights */}
      {insights?.insights?.length > 0 && (
        <div className="card" style={styles.insightsCard}>
          <h3 style={styles.cardTitle}>🤖 AI Insights</h3>
          <ul style={styles.insightsList}>
            {insights.insights.map((insight, i) => (
              <li key={i} style={styles.insightItem}>
                <span style={styles.insightDot} />
                {insight}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length === 0 ? (
        <div className="card" style={styles.emptyCard}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎉</div>
          <h3 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Great job!</h3>
          <p style={{ color: 'var(--color-text-secondary)' }}>
            No recommendations right now. Your subscriptions look optimized!
          </p>
        </div>
      ) : (
        <div style={styles.recList}>
          {['high', 'medium', 'low'].map((priority) => {
            const recs = recommendations.filter((r) => r.priority === priority);
            if (recs.length === 0) return null;
            return (
              <div key={priority}>
                <h3 style={{ ...styles.priorityHeader, color: PRIORITY_COLORS[priority] }}>
                  {priority === 'high' ? '🚨' : priority === 'medium' ? '⚠️' : '💡'}
                  {' '}{priority.charAt(0).toUpperCase() + priority.slice(1)} Priority
                </h3>
                <div style={styles.recGrid}>
                  {recs.map((rec) => (
                    <RecommendationCard key={rec.id} rec={rec} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function RecommendationCard({ rec }) {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div
      className="card"
      style={{
        ...styles.recCard,
        borderLeftColor: PRIORITY_COLORS[rec.priority] || '#94a3b8',
      }}
    >
      <div style={styles.recTop}>
        <span style={styles.actionIcon}>{ACTION_ICONS[rec.action] || '💡'}</span>
        <div style={{ flex: 1 }}>
          <div style={styles.recTitle}>{rec.title}</div>
          <span
            style={{
              ...styles.priorityBadge,
              background: PRIORITY_BG[rec.priority] || '#f1f5f9',
              color: PRIORITY_COLORS[rec.priority] || '#64748b',
            }}
          >
            {rec.priority}
          </span>
        </div>
        <button
          className="btn btn-sm btn-ghost"
          onClick={() => setDismissed(true)}
          style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}
        >
          ✕
        </button>
      </div>
      <p style={styles.recMessage}>{rec.message}</p>
      {rec.potential_savings > 0 && (
        <div style={styles.savings}>
          <span style={styles.savingsLabel}>Potential savings:</span>
          <span style={styles.savingsAmount}>
            ₹{rec.potential_savings.toLocaleString('en-IN', { maximumFractionDigits: 0 })}/month
          </span>
        </div>
      )}
      <div style={styles.recReason}>💬 {rec.reason}</div>
    </div>
  );
}

const styles = {
  page: { display: 'flex', flexDirection: 'column', gap: '1.25rem' },
  title: { fontSize: '1.75rem', fontWeight: '700' },
  subtitle: { color: 'var(--color-text-secondary)', fontSize: '0.9rem' },
  cardTitle: { fontSize: '1rem', fontWeight: '600', marginBottom: '1rem' },
  insightsCard: {
    background: 'linear-gradient(135deg, #ede9fe, #e0e7ff)',
    border: '1px solid #c7d2fe',
  },
  insightsList: { listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.625rem' },
  insightItem: { display: 'flex', alignItems: 'flex-start', gap: '0.625rem', fontSize: '0.9rem', color: '#3730a3' },
  insightDot: { width: '6px', height: '6px', borderRadius: '50%', background: '#6366f1', flexShrink: 0, marginTop: '0.45rem' },
  emptyCard: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '3rem', textAlign: 'center' },
  recList: { display: 'flex', flexDirection: 'column', gap: '1.5rem' },
  priorityHeader: { fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' },
  recGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '1rem',
  },
  recCard: {
    borderLeft: '4px solid',
    display: 'flex', flexDirection: 'column', gap: '0.75rem',
  },
  recTop: { display: 'flex', alignItems: 'flex-start', gap: '0.75rem' },
  actionIcon: { fontSize: '1.5rem', flexShrink: 0 },
  recTitle: { fontSize: '0.9rem', fontWeight: '600', color: 'var(--color-text)', marginBottom: '0.25rem' },
  priorityBadge: {
    display: 'inline-block', padding: '0.125rem 0.5rem', borderRadius: '999px',
    fontSize: '0.7rem', fontWeight: '600', textTransform: 'capitalize',
  },
  recMessage: { fontSize: '0.875rem', color: 'var(--color-text-secondary)', lineHeight: 1.6 },
  savings: { display: 'flex', alignItems: 'center', gap: '0.5rem' },
  savingsLabel: { fontSize: '0.8rem', color: 'var(--color-text-secondary)' },
  savingsAmount: { fontSize: '0.9rem', fontWeight: '700', color: '#10b981' },
  recReason: { fontSize: '0.75rem', color: 'var(--color-text-muted)', fontStyle: 'italic' },
};
