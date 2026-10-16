import { api, formatDate, formatTime, initials, rupees } from '../api';
import { Avatar, Empty, ErrorBanner, PageHeader, StatCard, StateBadge } from '../components/ui';
import { useAsync } from '../useAsync';

export default function Dashboard({ navigate }) {
  const { data, error, loading } = useAsync(() =>
    Promise.all([api.stats(), api.members.list({ state: 'EXPIRING_SOON' }), api.checkins.list({ limit: 6 })])
  );
  const [stats, expiring, recent] = data || [null, [], []];
  const maxPlan = Math.max(1, ...(stats?.plan_breakdown || []).map((p) => p.members));
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <>
      <PageHeader
        eyebrow="GYM / OVERVIEW"
        title={`${greeting} 💪`}
        subtitle="Here’s how IronPulse is doing today — served from AWS EKS (ap-south-1)."
        action={<button className="primary" onClick={() => navigate('attendance')}>⚡ Quick check-in</button>}
      />
      <ErrorBanner message={error} />

      <section className="stats">
        <StatCard label="Total members" value={loading ? '…' : stats?.total_members ?? 0} hint="All time" icon="👥" />
        <StatCard label="Active members" value={stats?.active_members ?? '…'} hint={`${stats?.expired_members ?? 0} expired`} icon="✅" tone="green" />
        <StatCard label="Check-ins today" value={stats?.checkins_today ?? '…'} hint="Since midnight" icon="🏋️" tone="blue" />
        <StatCard label="Monthly revenue" value={stats ? rupees(stats.monthly_revenue) : '…'} hint="Recurring, active plans" icon="₹" tone="amber" />
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="panel-head">
            <div>
              <h2>Memberships expiring soon</h2>
              <p className="muted">Reach out before they lapse.</p>
            </div>
            <button className="ghost" onClick={() => navigate('members')}>View all →</button>
          </div>
          {expiring.length ? (
            <ul className="list">
              {expiring.map((m) => (
                <li key={m.id}>
                  <Avatar text={initials(m.full_name)} />
                  <div className="grow">
                    <b>{m.full_name}</b>
                    <small>{m.plan_name} · ends {formatDate(m.end_date)}</small>
                  </div>
                  <StateBadge state={m.membership_state} />
                </li>
              ))}
            </ul>
          ) : (
            <Empty>{loading ? 'Loading…' : 'No memberships expire in the next 7 days 🎉'}</Empty>
          )}

          <div className="panel-head subtle">
            <div>
              <h2>Members by plan</h2>
              <p className="muted">{stats?.plans ?? 0} plans · {stats?.trainers ?? 0} trainers on staff</p>
            </div>
          </div>
          <div className="bars">
            {(stats?.plan_breakdown || []).map((p) => (
              <div className="bar-row" key={p.plan}>
                <span>{p.plan}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${(p.members / maxPlan) * 100}%` }} />
                </div>
                <b>{p.members}</b>
              </div>
            ))}
            {!stats?.plan_breakdown?.length && <Empty>No plans yet.</Empty>}
          </div>
        </div>

        <aside className="panel">
          <div className="panel-head">
            <div>
              <h2>Recent check-ins</h2>
              <p className="muted">Latest visits at the front desk.</p>
            </div>
          </div>
          {recent.length ? (
            <ul className="list">
              {recent.map((c) => (
                <li key={c.id}>
                  <span className="activity-icon">✓</span>
                  <div className="grow">
                    <b>{c.member_name}</b>
                    <small>{formatTime(c.checked_in_at)}</small>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <Empty>{loading ? 'Loading…' : 'No check-ins yet today.'}</Empty>
          )}
          <div className="pipeline" title="How this app ships">
            <span>Test</span><i /><span>Build</span><i /><span>Scan</span><i /><span>Deploy</span>
          </div>
        </aside>
      </section>
    </>
  );
}
