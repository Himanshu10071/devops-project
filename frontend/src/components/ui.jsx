import { useEffect } from 'react';

export function Modal({ title, eyebrow, onClose, children }) {
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={title}>
        <div className="modal-head">
          <div>
            {eyebrow && <p className="eyebrow">{eyebrow}</p>}
            <h2>{title}</h2>
          </div>
          <button type="button" className="close" onClick={onClose} aria-label="Close">×</button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function StatCard({ label, value, hint, icon, tone = 'default' }) {
  return (
    <div className={`stat tone-${tone}`}>
      <div className="stat-icon" aria-hidden="true">{icon}</div>
      <div>
        <small>{label}</small>
        <strong>{value}</strong>
        {hint && <span>{hint}</span>}
      </div>
    </div>
  );
}

const STATE_LABELS = {
  ACTIVE: 'Active',
  EXPIRING_SOON: 'Expiring soon',
  EXPIRED: 'Expired',
  FROZEN: 'Frozen',
  CANCELLED: 'Cancelled',
};

export function StateBadge({ state }) {
  return <span className={`badge state-${state.toLowerCase()}`}>{STATE_LABELS[state] || state}</span>;
}

export function Avatar({ text, size = 'md' }) {
  return <div className={`avatar avatar-${size}`}>{text}</div>;
}

export function PageHeader({ eyebrow, title, subtitle, action }) {
  return (
    <header className="page-header">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {subtitle && <p className="muted">{subtitle}</p>}
      </div>
      {action}
    </header>
  );
}

export function Empty({ children }) {
  return <div className="empty">{children}</div>;
}

export function ErrorBanner({ message }) {
  if (!message) return null;
  return (
    <div className="alert" role="alert">
      ⚠ {message}
    </div>
  );
}
