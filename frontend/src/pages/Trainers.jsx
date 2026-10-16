import { useState } from 'react';
import { api, initials } from '../api';
import { Avatar, Empty, ErrorBanner, Modal, PageHeader } from '../components/ui';
import { useAsync } from '../useAsync';

export default function Trainers({ notify }) {
  const { data: trainers, error, loading, reload, setError } = useAsync(() => api.trainers.list());
  const [editing, setEditing] = useState(null);

  const remove = async (t) => {
    if (!window.confirm(`Remove ${t.name}? Their members will be unassigned.`)) return;
    try {
      await api.trainers.remove(t.id);
      notify('Trainer removed');
      reload();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <>
      <PageHeader
        eyebrow="GYM / TRAINERS"
        title="Trainers"
        subtitle="Coaching staff and the members assigned to them."
        action={<button className="primary" onClick={() => setEditing({})}>＋ New trainer</button>}
      />
      <ErrorBanner message={error} />
      {loading ? (
        <Empty>Loading trainers…</Empty>
      ) : (
        <section className="card-grid">
          {(trainers || []).map((t) => (
            <article className="panel trainer-card" key={t.id}>
              <div className="person">
                <Avatar text={initials(t.name)} size="lg" />
                <div>
                  <h2>{t.name}</h2>
                  <small className="muted">{t.specialization}</small>
                </div>
              </div>
              <dl>
                <div><dt>Experience</dt><dd>{t.experience_years} yrs</dd></div>
                <div><dt>Members</dt><dd>{t.member_count}</dd></div>
              </dl>
              <p className="muted contact">{t.email || 'No email'}{t.phone && ` · ${t.phone}`}</p>
              <div className="card-actions">
                <button className="ghost" onClick={() => setEditing(t)}>Edit</button>
                <button className="ghost danger" onClick={() => remove(t)}>Remove</button>
              </div>
            </article>
          ))}
          {!trainers?.length && <Empty>No trainers yet.</Empty>}
        </section>
      )}

      {editing && (
        <Modal title={editing.id ? `Edit ${editing.name}` : 'Add a trainer'} eyebrow="TRAINER" onClose={() => setEditing(null)}>
          <TrainerForm
            trainer={editing}
            onSaved={(message) => {
              setEditing(null);
              notify(message);
              reload();
            }}
          />
        </Modal>
      )}
    </>
  );
}

function TrainerForm({ trainer, onSaved }) {
  const [error, setError] = useState('');
  const submit = async (e) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const body = {
      name: f.get('name'),
      specialization: f.get('specialization'),
      email: f.get('email'),
      phone: f.get('phone'),
      experience_years: Number(f.get('experience_years')),
    };
    try {
      if (trainer.id) await api.trainers.update(trainer.id, body);
      else await api.trainers.create(body);
      onSaved(trainer.id ? 'Trainer updated' : `${body.name} added to the team`);
    } catch (err) {
      setError(err.message);
    }
  };
  return (
    <form onSubmit={submit}>
      <ErrorBanner message={error} />
      <label>Name<input name="name" required defaultValue={trainer.name} placeholder="e.g. Kavya Iyer" /></label>
      <div className="form-row">
        <label>Specialization<input name="specialization" defaultValue={trainer.specialization ?? 'General Fitness'} /></label>
        <label>Experience (years)<input name="experience_years" type="number" min="0" max="60" defaultValue={trainer.experience_years ?? 0} /></label>
      </div>
      <div className="form-row">
        <label>Email<input name="email" type="email" defaultValue={trainer.email} /></label>
        <label>Phone<input name="phone" defaultValue={trainer.phone} /></label>
      </div>
      <button className="primary full">{trainer.id ? 'Save trainer' : 'Add trainer'}</button>
    </form>
  );
}
