// All calls go to a relative /api path. Nginx (Docker) or the Ingress (Kubernetes)
// routes them to the FastAPI backend, so the browser never needs the backend host.
const BASE = '/api';

async function request(path, { method = 'GET', body } = {}) {
  const response = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => `${d.loc?.slice(-1)[0]}: ${d.msg}`).join(', ')
      : detail || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return data;
}

const crud = (resource) => ({
  list: (params) => request(`/${resource}${params ? `?${new URLSearchParams(params)}` : ''}`),
  get: (id) => request(`/${resource}/${id}`),
  create: (body) => request(`/${resource}`, { method: 'POST', body }),
  update: (id, body) => request(`/${resource}/${id}`, { method: 'PUT', body }),
  remove: (id) => request(`/${resource}/${id}`, { method: 'DELETE' }),
});

export const api = {
  plans: crud('plans'),
  trainers: crud('trainers'),
  members: { ...crud('members'), renew: (id) => request(`/members/${id}/renew`, { method: 'POST' }) },
  checkins: {
    list: (params) => request(`/checkins?${new URLSearchParams(params || {})}`),
    create: (memberId) => request('/checkins', { method: 'POST', body: { member_id: memberId } }),
  },
  stats: () => request('/dashboard/stats'),
};

export const rupees = (value) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value || 0);

export const formatDate = (iso) =>
  iso ? new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—';

export const formatTime = (iso) =>
  new Date(iso).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });

export const initials = (name = '') =>
  name.split(' ').filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join('');
