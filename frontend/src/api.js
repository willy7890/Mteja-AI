import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000", // badilisha kama una domain nyingine
});

// Ongeza token kila request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Kama token imeisha → toa na rudisha login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login"; // badilisha path yako ya login
    }
    return Promise.reject(error);
  }
);

export default api;