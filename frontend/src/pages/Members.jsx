import { useState } from 'react';
import { api, formatDate, initials } from '../api';
import { Avatar, Empty, ErrorBanner, Modal, PageHeader, StateBadge } from '../components/ui';
import { useAsync } from '../useAsync';

const FILTERS = [
  ['ALL', 'All'],
  ['ACTIVE', 'Active'],
  ['EXPIRING_SOON', 'Expiring'],
  ['EXPIRED', 'Expired'],
  ['FROZEN', 'Frozen'],
];

export default function Members({ notify }) {
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');
  const [editing, setEditing] = useState(null); // null = closed, {} = new, member = edit

  const { data, error, loading, reload, setError } = useAsync(
    () =>
      Promise.all([
        api.members.list({ ...(filter !== 'ALL' && { state: filter }), ...(search && { q: search }) }),
        api.plans.list(),
        api.trainers.list(),
      ]),
    [filter, search]
  );
  const [members, plans, trainers] = data || [[], [], []];

  const run = async (action, message) => {
    try {
      await action();
      notify(message);
      reload();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <>
      <PageHeader
        eyebrow="GYM / MEMBERS"
        title="Members"
        subtitle="Register members, renew plans and manage memberships."
        action={<button className="primary" onClick={() => setEditing({})}>＋ New member</button>}
      />
      <ErrorBanner message={error} />

      <div className="panel">
        <div className="panel-head wrap">
          <input
            className="search"
            type="search"
            placeholder="Search name, email or phone…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <div className="filters">
            {FILTERS.map(([key, label]) => (
              <button key={key} className={filter === key ? 'selected' : ''} onClick={() => setFilter(key)}>
                {label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <Empty>Loading members…</Empty>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Member</th>
                  <th>Plan</th>
                  <th>Trainer</th>
                  <th>Valid till</th>
                  <th>Status</th>
                  <th className="right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {members.map((m) => (
                  <tr key={m.id}>
                    <td data-label="Member">
                      <div className="person">
                        <Avatar text={initials(m.full_name)} />
                        <div>
                          <b>{m.full_name}</b>
                          <small>{m.email}{m.phone && ` · ${m.phone}`}</small>
                        </div>
                      </div>
                    </td>
                    <td data-label="Plan">{m.plan_name || '—'}</td>
                    <td data-label="Trainer">{m.trainer_name || <span className="muted">Unassigned</span>}</td>
                    <td data-label="Valid till">
                      <div>
                        {formatDate(m.end_date)}
                        <small className="block muted">{m.days_left} days left</small>
                      </div>
                    </td>
                    <td data-label="Status"><StateBadge state={m.membership_state} /></td>
                    <td className="right actions">
                      <button className="icon-btn" title="Check in" onClick={() => run(() => api.checkins.create(m.id), `${m.full_name} checked in`)}>✓</button>
                      <button className="icon-btn" title="Renew plan" onClick={() => run(() => api.members.renew(m.id), `Membership renewed for ${m.full_name}`)}>↻</button>
                      <button className="icon-btn" title="Edit" onClick={() => setEditing(m)}>✎</button>
                      <button
                        className="icon-btn danger"
                        title="Delete"
                        onClick={() => window.confirm(`Delete ${m.full_name}?`) && run(() => api.members.remove(m.id), 'Member deleted')}
                      >
                        🗑
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!members.length && <Empty>No members match this view.</Empty>}
          </div>
        )}
      </div>

      {editing && (
        <MemberForm
          member={editing}
          plans={plans}
          trainers={trainers}
          onClose={() => setEditing(null)}
          onSaved={(message) => {
            setEditing(null);
            notify(message);
            reload();
          }}
        />
      )}
    </>
  );
}

function MemberForm({ member, plans, trainers, onClose, onSaved }) {
  const isNew = !member.id;
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const body = {
      full_name: f.get('full_name'),
      email: f.get('email'),
      phone: f.get('phone'),
      gender: f.get('gender'),
      plan_id: Number(f.get('plan_id')),
      trainer_id: f.get('trainer_id') ? Number(f.get('trainer_id')) : null,
      start_date: f.get('start_date') || null,
    };
    if (!isNew) body.status = f.get('status');
    try {
      if (isNew) await api.members.create(body);
      else await api.members.update(member.id, body);
      onSaved(isNew ? `${body.full_name} joined IronPulse` : 'Member updated');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Modal title={isNew ? 'Register a member' : `Edit ${member.full_name}`} eyebrow={isNew ? 'NEW MEMBER' : 'EDIT MEMBER'} onClose={onClose}>
      <form onSubmit={submit}>
        <ErrorBanner message={error} />
        <label>Full name<input name="full_name" required defaultValue={member.full_name} placeholder="e.g. Ananya Gupta" /></label>
        <div className="form-row">
          <label>Email<input name="email" type="email" required defaultValue={member.email} placeholder="ananya@example.com" /></label>
          <label>Phone<input name="phone" defaultValue={member.phone} placeholder="98765 43210" /></label>
        </div>
        <div className="form-row">
          <label>
            Plan
            <select name="plan_id" required defaultValue={member.plan_id ?? plans[0]?.id}>
              {plans.map((p) => (
                <option key={p.id} value={p.id}>{p.name} — ₹{p.price} / {p.duration_months} mo</option>
              ))}
            </select>
          </label>
          <label>
            Trainer
            <select name="trainer_id" defaultValue={member.trainer_id ?? ''}>
              <option value="">No trainer</option>
              {trainers.map((t) => (
                <option key={t.id} value={t.id}>{t.name} ({t.specialization})</option>
              ))}
            </select>
          </label>
        </div>
        <div className="form-row">
          <label>
            Gender
            <select name="gender" defaultValue={member.gender || 'OTHER'}>
              <option value="MALE">Male</option>
              <option value="FEMALE">Female</option>
              <option value="OTHER">Other</option>
            </select>
          </label>
          <label>Start date<input name="start_date" type="date" defaultValue={member.start_date} /></label>
        </div>
        {!isNew && (
          <label>
            Status
            <select name="status" defaultValue={member.status}>
              <option value="ACTIVE">Active</option>
              <option value="FROZEN">Frozen (paused)</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </label>
        )}
        {!plans.length && <p className="muted">Create a membership plan first.</p>}
        <button className="primary full" disabled={!plans.length}>{isNew ? 'Register member' : 'Save changes'}</button>
      </form>
    </Modal>
  );
}
