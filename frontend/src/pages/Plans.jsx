import { useState } from 'react';
import { api, rupees } from '../api';
import { Empty, ErrorBanner, Modal, PageHeader } from '../components/ui';
import { useAsync } from '../useAsync';

export default function Plans({ notify }) {
  const { data: plans, error, loading, reload, setError } = useAsync(() => api.plans.list());
  const [editing, setEditing] = useState(null);

  const remove = async (plan) => {
    if (!window.confirm(`Delete the ${plan.name} plan?`)) return;
    try {
      await api.plans.remove(plan.id);
      notify('Plan deleted');
      reload();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <>
      <PageHeader
        eyebrow="GYM / PLANS"
        title="Membership plans"
        subtitle="Pricing and duration for every membership you sell."
        action={<button className="primary" onClick={() => setEditing({})}>＋ New plan</button>}
      />
      <ErrorBanner message={error} />
      {loading ? (
        <Empty>Loading plans…</Empty>
      ) : (
        <section className="card-grid">
          {(plans || []).map((p) => (
            <article className="panel plan-card" key={p.id}>
              <p className="eyebrow">{p.duration_months} MONTH{p.duration_months > 1 ? 'S' : ''}</p>
              <h2>{p.name}</h2>
              <p className="price">{rupees(p.price)}</p>
              <p className="muted">{rupees(Math.round(p.price / p.duration_months))} / month</p>
              <p className="description">{p.description || 'No description'}</p>
              <div className="card-actions">
                <button className="ghost" onClick={() => setEditing(p)}>Edit</button>
                <button className="ghost danger" onClick={() => remove(p)}>Delete</button>
              </div>
            </article>
          ))}
          {!plans?.length && <Empty>No plans yet — create your first one.</Empty>}
        </section>
      )}

      {editing && (
        <Modal title={editing.id ? `Edit ${editing.name}` : 'Create a plan'} eyebrow="MEMBERSHIP PLAN" onClose={() => setEditing(null)}>
          <PlanForm
            plan={editing}
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

function PlanForm({ plan, onSaved }) {
  const [error, setError] = useState('');
  const submit = async (e) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const body = {
      name: f.get('name'),
      duration_months: Number(f.get('duration_months')),
      price: Number(f.get('price')),
      description: f.get('description'),
    };
    try {
      if (plan.id) await api.plans.update(plan.id, body);
      else await api.plans.create(body);
      onSaved(plan.id ? 'Plan updated' : `${body.name} plan created`);
    } catch (err) {
      setError(err.message);
    }
  };
  return (
    <form onSubmit={submit}>
      <ErrorBanner message={error} />
      <label>Plan name<input name="name" required defaultValue={plan.name} placeholder="e.g. Student Monthly" /></label>
      <div className="form-row">
        <label>Duration (months)<input name="duration_months" type="number" min="1" max="36" required defaultValue={plan.duration_months ?? 1} /></label>
        <label>Price (₹)<input name="price" type="number" min="0" required defaultValue={plan.price ?? 1500} /></label>
      </div>
      <label>Description<textarea name="description" defaultValue={plan.description} placeholder="What’s included?" /></label>
      <button className="primary full">{plan.id ? 'Save plan' : 'Create plan'}</button>
    </form>
  );
}
