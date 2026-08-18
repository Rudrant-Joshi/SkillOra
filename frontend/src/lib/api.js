/**
 * API client — connects the frontend to the backend REST API.
 * Handles JWT token persistence, auth header injection, and error handling.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const TOKEN_KEY = 'skillgraph_auth_token_v1';

function getToken() {
  try {
    const session = localStorage.getItem('skillgraph_demo_session_v1');
    if (session) {
      const parsed = JSON.parse(session);
      if (parsed.token) return parsed.token;
    }
  } catch (e) {
    // fall through
  }
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem('skillgraph_demo_session_v1');
}

async function request(path, { method = 'GET', body, headers = {}, token = true } = {}) {
  const url = `${BASE_URL}${path}`;
  const opts = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  };
  if (token) {
    const t = getToken();
    if (t) {
      opts.headers.Authorization = `Bearer ${t}`;
    }
  }
  if (body !== undefined) {
    opts.body = JSON.stringify(body);
  }

  const resp = await fetch(url, opts);
  const data = await resp.json().catch(() => ({}));

  if (!resp.ok) {
    const error = new Error(data.detail || data.message || `HTTP ${resp.status}`);
    error.status = resp.status;
    error.data = data;
    throw error;
  }
  return data;
}

/**
 * Returns { ok: true, data } or { ok: false, error, status }.
 * Use this in React components that want to handle offline gracefully.
 */
async function safeRequest(path, options) {
  try {
    const data = await request(path, options);
    return { ok: true, data };
  } catch (e) {
    return { ok: false, error: e.message, status: e.status, data: e.data };
  }
}

export const api = {
  // Auth
  login: (email, password) => request('/api/auth/login', { method: 'POST', body: { email, password }, token: false }),
  signup: (payload) => request('/api/auth/signup', { method: 'POST', body: payload, token: false }),
  getRoles: () => request('/api/auth/roles', { token: false }),
  getMe: () => request('/api/auth/me'),

  // Assessments
  listAssessments: (params = {}) => {
    const qs = new URLSearchParams();
    if (params.active_only !== undefined) qs.set('active_only', params.active_only);
    if (params.company_id !== undefined) qs.set('company_id', params.company_id);
    const query = qs.toString();
    return request(`/api/assessments/${query ? `?${query}` : ''}`);
  },
  getAssessment: (id) => request(`/api/assessments/${id}`),
  startAssessment: (id) => request(`/api/assessments/${id}/start`, { method: 'POST' }),
  getQuestions: (id, attemptId) => {
    const qs = new URLSearchParams();
    if (attemptId) qs.set('attempt_id', attemptId);
    const q = qs.toString();
    return request(`/api/assessments/${id}/questions${q ? `?${q}` : ''}`);
  },
  listAttempts: (id) => request(`/api/assessments/${id}/attempts`),

  // Attempts
  submitAnswers: (attemptId, answers) => request(`/api/attempts/${attemptId}/submit`, {
    method: 'POST',
    body: { answers },
  }),
  getAttempt: (attemptId) => request(`/api/attempts/${attemptId}`),
  getAttemptAnswers: (attemptId) => request(`/api/attempts/${attemptId}/answers`),
  listUserAttempts: (userId) => request(`/api/attempts/user/${userId}`),

  // Skills
  getMySkills: () => request('/api/skills/me'),
  getUserSkills: (userId) => request(`/api/skills/user/${userId}`),
  listSkills: (category) => request(`/api/skills/${category ? `?category=${category}` : ''}`),

  // Analytics (trainer/admin)
  dashboardAnalytics: () => request('/api/analytics/dashboard'),
  assessmentAnalytics: (assessmentId) => request(`/api/analytics/assessment/${assessmentId}`),
  candidateAnalytics: (userId) => request(`/api/analytics/candidate/${userId}`),
  skillGaps: () => request('/api/analytics/skill-gaps'),

  // Offline sync
  syncOffline: (payloads) => request('/api/offline/sync', { method: 'POST', body: payloads }),

  // ML analytics
  mlAnalyticsSummary: () => request('/api/analytics/ml'),

  // Internal
  getToken,
  setToken,
  clearToken,
  safeRequest,
  isOnline: () => !!getToken(),
};
