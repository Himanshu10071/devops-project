import { useCallback, useEffect, useState } from 'react';

// Loads data on mount and exposes reload() so pages can refresh after a mutation.
export function useAsync(loader, deps = []) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const reload = useCallback(async () => {
    try {
      setError('');
      setData(await loader());
    } catch (e) {
      setError(e.message === 'Failed to fetch' ? 'Backend unavailable — start the API and PostgreSQL' : e.message);
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => {
    reload();
  }, [reload]);

  return { data, error, loading, reload, setError };
}
