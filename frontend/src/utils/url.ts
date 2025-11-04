const DEFAULT_API_BASE = 'http://localhost:8000/api/v1';

function computeStaticBase(): string {
  const baseValue = import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE;
  try {
    const baseUrl = new URL(baseValue);
    const origin = `${baseUrl.protocol}//${baseUrl.host}`;
    const trimmed = baseUrl.pathname.replace(/\/api\/v1\/?$/, '');
    if (!trimmed || trimmed === '/') {
      return origin;
    }
    return `${origin}${trimmed.endsWith('/') ? trimmed.slice(0, -1) : trimmed}`;
  } catch {
    return DEFAULT_API_BASE.replace(/\/api\/v1\/?$/, '');
  }
}

const STATIC_BASE = computeStaticBase();

export function resolveStaticUrl(path?: string | null): string | null {
  if (!path) {
    return null;
  }
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${STATIC_BASE}${normalized}`;
}
