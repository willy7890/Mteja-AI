import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 1. Request Interceptor: Inaweka Access Token kwenye kila Request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 2. Response Interceptor: Inahandle Token Refresh pindi 401 inapotokea
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Zuia kuingia kwenye loop kama request tayari ilikuwa ni ya /auth/login au /auth/refresh
    if (
      originalRequest.url?.includes("/auth/login") ||
      originalRequest.url?.includes("/auth/refresh")
    ) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
          clearTokensAndRedirect();
          return Promise.reject(error);
        }

        // Tuma Body yenye structure inayoeleweka badala ya `{}`
        const res = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token } = res.data;

        localStorage.setItem("access_token", access_token);
        if (refresh_token) {
          localStorage.setItem("refresh_token", refresh_token);
        }

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        clearTokensAndRedirect();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

function clearTokensAndRedirect() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  if (window.location.pathname !== "/login") {
    window.location.href = "/login";
  }
}

export default api;