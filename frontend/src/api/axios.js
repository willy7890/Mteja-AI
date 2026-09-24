import axios from "axios";

const api = axios.create({
  baseURL: `${(
    import.meta.env.VITE_API_URL ||
    import.meta.env.VITE_API_BASE_URL ||
    (typeof window !== "undefined" && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1"
      ? "https://mteja-ai-upyg.onrender.com"
      : "http://127.0.0.1:8000")
  ).replace(/\/$/, "")}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
