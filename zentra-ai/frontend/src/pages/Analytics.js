import React, { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area, Legend,
} from 'recharts';

const CATEGORY_COLORS = {
  streaming: '#ef4444', music: '#8b5cf6', productivity: '#3b82f6',
  cloud_storage: '#0ea5e9', fitness: '#10b981', gaming: '#f59e0b',
  food: '#f97316', education: '#14b8a6', communication: '#6366f1',
  security: '#64748b', other: '#94a3b8',
};

export default function Analytics() {
  const [summary, setSummary] = useState(null);
  const [categoryData, setCategoryData] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [savings, setSavings] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsAPI.summary(),
      analyticsAPI.categoryBreakdown(),
      analyticsAPI.monthlyTrend(6),
      analyticsAPI.savingsPotential(),
    ]).then(([s, c, t, sv]) => {
      setSummary(s.data);
      setCategoryData(c.data);
      setTrendData(t.data);
      setSavings(sv.data);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div style={styles.loadingCenter}><div className="spinner" style={{ width: 40, height: 40 }} /></div>;
  }

  const pieData = categoryData.map((c) => ({
    name: c.category.replace('_', ' '),
    value: c.monthly_amount,
    color: CATEGORY_COLORS[c.category] || '#94a3b8',
  }));

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>Analytics</h1>
      <p style={styles.subtitle}>Detailed spending analysis and trends</p>

      {/* Summary Cards */}
      <div className="grid-4">
        <StatCard label="Monthly Spend" value={`₹${(summary?.total_monthly_spend || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`} icon="💳" color="#6366f1" />
        <StatCard label="Annual Spend" value={`₹${(summary?.total_annual_spend || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`} icon="📅" color="#8b5cf6" />
        <StatCard label="Active Services" value={summary?.active_count || 0} icon="✅" color="#10b981" />
        <StatCard label="Potential Savings" value={`₹${(savings?.total_potential_savings || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`} icon="💰" color="#f59e0b" />
      </div>

      {/* Savings Breakdown */}
      {savings && savings.total_potential_savings > 0 && (
        <div className="card" style={styles.savingsCard}>
          <h3 style={styles.cardTitle}>💰 Savings Opportunity</h3>
          <div style={styles.savingsGrid}>
            <SavingsItem label="Unused subscriptions" amount={savings.unused_savings} color="#ef4444" />
            <SavingsItem label="Duplicate services" amount={savings.duplicate_savings} color="#f59e0b" />
            <SavingsItem label="Total potential savings" amount={savings.total_potential_savings} color="#10b981" bold />
          </div>
          <div style={styles.savingsBar}>
            <div style={{ ...styles.savingsBarFill, width: `${savings.savings_percentage}%` }} />
          </div>
          <p style={styles.savingsText}>
            You could save up to {savings.savings_percentage}% of your monthly spend
          </p>
        </div>
      )}

      {/* Charts */}
      <div style={styles.chartsRow}>
        {/* Monthly Trend */}
        <div className="card" style={{ flex: 2 }}>
          <h3 style={styles.cardTitle}>Monthly Spending Trend</h3>
          {trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
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
                  type="monotone" dataKey="total_spend" stroke="#6366f1"
                  strokeWidth={2} fill="url(#areaGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart />
          )}
        </div>

        {/* Category Pie */}
        <div className="card" style={{ flex: 1, minWidth: '240px' }}>
          <h3 style={styles.cardTitle}>By Category</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%" cy="50%"
                  innerRadius={60} outerRadius={90}
                  paddingAngle={3} dataKey="value"
                >
                  {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip formatter={(v) => [`₹${v.toLocaleString('en-IN')}`, 'Spend']} contentStyle={{ borderRadius: '8px', fontSize: '0.875rem' }} />
                <Legend formatter={(v) => <span style={{ fontSize: '0.75rem' }}>{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart />
          )}
        </div>
      </div>

      {/* Category Bar Chart */}
      {categoryData.length > 0 && (
        <div className="card">
          <h3 style={styles.cardTitle}>Spending by Category (Monthly)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={categoryData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="category" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(v) => [`₹${v.toLocaleString('en-IN')}`, 'Monthly']}
                contentStyle={{ borderRadius: '8px', fontSize: '0.875rem' }}
              />
              <Bar dataKey="monthly_amount" radius={[4, 4, 0, 0]}>
                {categoryData.map((entry, i) => (
                  <Cell key={i} fill={CATEGORY_COLORS[entry.category] || '#6366f1'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Category Detail Table */}
      {categoryData.length > 0 && (
        <div className="card">
          <h3 style={styles.cardTitle}>Category Breakdown</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={styles.table}>
              <thead>
                <tr style={styles.tableHead}>
                  <th>Category</th>
                  <th>Services</th>
                  <th>Count</th>
                  <th>Monthly</th>
                  <th>Share</th>
                </tr>
              </thead>
              <tbody>
                {categoryData.map((row, i) => (
                  <tr key={i} style={i % 2 === 0 ? styles.tableRowEven : {}}>
                    <td style={styles.tableCell}>
                      <span style={{ ...styles.categoryDot, background: CATEGORY_COLORS[row.category] || '#94a3b8' }} />
                      {row.category.replace('_', ' ')}
                    </td>
                    <td style={styles.tableCell}>{row.services?.slice(0, 2).join(', ')}{row.services?.length > 2 ? `+${row.services.length - 2}` : ''}</td>
                    <td style={styles.tableCell}>{row.count}</td>
                    <td style={styles.tableCell}>₹{row.monthly_amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</td>
                    <td style={styles.tableCell}>
                      <div style={styles.progressWrap}>
                        <div style={{ ...styles.progressBar, width: `${row.percentage}%`, background: CATEGORY_COLORS[row.category] || '#6366f1' }} />
                        <span style={styles.progressLabel}>{row.percentage}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, icon, color }) {
  return (
    <div className="stat-card">
      <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>{icon}</div>
      <div style={{ fontSize: '1.5rem', fontWeight: '700', color }}>{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function SavingsItem({ label, amount, color, bold }) {
  return (
    <div style={styles.savingsItem}>
      <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>{label}</span>
      <span style={{ color, fontWeight: bold ? '700' : '600', fontSize: bold ? '1.1rem' : '0.9rem' }}>
        ₹{amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
      </span>
    </div>
  );
}

function EmptyChart() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px', color: 'var(--color-text-muted)' }}>
      No data yet
    </div>
  );
}

const styles = {
  page: { display: 'flex', flexDirection: 'column', gap: '1.25rem' },
  loadingCenter: { display: 'flex', justifyContent: 'center', padding: '3rem' },
  title: { fontSize: '1.75rem', fontWeight: '700', marginBottom: '0.25rem' },
  subtitle: { color: 'var(--color-text-secondary)', fontSize: '0.9rem', marginBottom: '0.25rem' },
  cardTitle: { fontSize: '1rem', fontWeight: '600', marginBottom: '1rem' },
  chartsRow: { display: 'flex', gap: '1.25rem', flexWrap: 'wrap' },
  savingsCard: { background: 'linear-gradient(135deg, #f0fdf4, #dcfce7)' },
  savingsGrid: { display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1rem' },
  savingsItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.375rem 0' },
  savingsBar: { height: '8px', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden', marginBottom: '0.5rem' },
  savingsBarFill: { height: '100%', background: 'linear-gradient(90deg, #10b981, #059669)', borderRadius: '4px', transition: 'width 0.5s' },
  savingsText: { fontSize: '0.8rem', color: '#065f46' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' },
  tableHead: { background: 'var(--color-bg)', textAlign: 'left' },
  tableCell: { padding: '0.75rem 0.875rem', borderBottom: '1px solid var(--color-border)', verticalAlign: 'middle' },
  tableRowEven: { background: 'var(--color-bg)' },
  categoryDot: { display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', marginRight: '0.5rem' },
  progressWrap: { display: 'flex', alignItems: 'center', gap: '0.5rem' },
  progressBar: { height: '6px', borderRadius: '3px', flexShrink: 0 },
  progressLabel: { fontSize: '0.75rem', color: 'var(--color-text-secondary)', whiteSpace: 'nowrap' },
};
