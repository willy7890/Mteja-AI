const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

function extractErrorMessage(data, fallback) {
  if (!data) return fallback;

  if (typeof data.detail === 'string') {
    return data.detail;
  }

  if (Array.isArray(data.detail)) {
    return data.detail
      .map((error) => error?.msg || 'Validation error')
      .join(', ');
  }

  return fallback;
}

function authHeader() {
  const token = localStorage.getItem('access_token');

  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

async function handleResponse(res) {
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }

    throw new ApiError(
      extractErrorMessage(
        data,
        `Request failed (${res.status})`
      ),
      res.status,
      data
    );
  }

  return data;
}

export async function apiPost(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  return handleResponse(res);
}

export async function apiPostForm(path, fields) {
  const body = new URLSearchParams();

  Object.entries(fields).forEach(([key, value]) => {
    body.append(key, value);
  });

  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: body.toString(),
  });

  return handleResponse(res);
}

export async function apiGet(path) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'GET',
    headers: {
      ...authHeader(),
    },
  });

  return handleResponse(res);
}

export async function apiAuthPost(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authHeader(),
    },
    body: JSON.stringify(body),
  });

  return handleResponse(res);
}

export async function apiAuthPatch(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      ...authHeader(),
    },
    body: JSON.stringify(body),
  });

  return handleResponse(res);
}

export async function apiAuthUpload(
  path,
  file,
  fields = {}
) {
  const body = new FormData();

  body.append('file', file);

  Object.entries(fields).forEach(([key, value]) => {
    body.append(key, String(value));
  });

  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      ...authHeader(),
    },
    body,
  });

  return handleResponse(res);
}

export function apiAssetUrl(path) {
  if (!path) return '';

  if (/^https?:\/\//i.test(path)) {
    return path;
  }

  return `${BASE_URL}${
    path.startsWith('/') ? path : `/${path}`
  }`;
}

export { ApiError };