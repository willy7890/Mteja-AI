import axios from "axios";

const api = axios.create({
  baseURL: `${(
    import.meta.env.VITE_API_URL ||
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000"
  ).replace(/\/$/, "")}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
