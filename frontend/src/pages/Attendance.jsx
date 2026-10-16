import { useState } from 'react';
import { api, formatTime, initials } from '../api';
import { Avatar, Empty, ErrorBanner, PageHeader, StateBadge } from '../components/ui';
import { useAsync } from '../useAsync';

export default function Attendance({ notify }) {
  const [query, setQuery] = useState('');
  const { data, error, loading, reload, setError } = useAsync(
    () => Promise.all([api.members.list(query ? { q: query } : undefined), api.checkins.list({ limit: 25 })]),
    [query]
  );
  const [members, checkins] = data || [[], []];

  const checkIn = async (member) => {
    try {
      await api.checkins.create(member.id);
      notify(`${member.full_name} checked in`);
      reload();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <>
      <PageHeader eyebrow="GYM / ATTENDANCE" title="Front desk" subtitle="Check members in as they arrive." />
      <ErrorBanner message={error} />
      <section className="content-grid">
        <div className="panel">
          <div className="panel-head">
            <input
              className="search"
              type="search"
              autoFocus
              placeholder="Find member by name, email or phone…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          {loading ? (
            <Empty>Loading…</Empty>
          ) : members.length ? (
            <ul className="list">
              {members.slice(0, 12).map((m) => {
                const allowed = m.membership_state === 'ACTIVE' || m.membership_state === 'EXPIRING_SOON';
                return (
                  <li key={m.id}>
                    <Avatar text={initials(m.full_name)} />
                    <div className="grow">
                      <b>{m.full_name}</b>
                      <small>{m.plan_name} · {m.days_left} days left</small>
                    </div>
                    <StateBadge state={m.membership_state} />
                    <button className="primary small" disabled={!allowed} onClick={() => checkIn(m)}>Check in</button>
                  </li>
                );
              })}
            </ul>
          ) : (
            <Empty>No members found.</Empty>
          )}
        </div>
        <aside className="panel">
          <div className="panel-head">
            <div>
              <h2>Visit log</h2>
              <p className="muted">Most recent {checkins.length} check-ins.</p>
            </div>
          </div>
          {checkins.length ? (
            <ul className="list">
              {checkins.map((c) => (
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
            <Empty>No visits recorded yet.</Empty>
          )}
        </aside>
      </section>
    </>
  );
}
