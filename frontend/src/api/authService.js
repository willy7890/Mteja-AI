import api from "./axios";

export const authService = {
  // Register
  register: async (data) => {
    const response = await api.post("/auth/register", data);
    return response.data;
  },

  // Login
  login: async (email, password) => {
    // Backend inatumia OAuth2PasswordRequestForm (form-data)
    const formData = new FormData();
    formData.append("username", email); // Swagger inatumia username
    formData.append("password", password);

    const response = await api.post("/auth/login", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    // Hifadhi tokens
    localStorage.setItem("access_token", response.data.access_token);
    localStorage.setItem("refresh_token", response.data.refresh_token);

    return response.data;
  },

  // Get current user
  getMe: async () => {
    const response = await api.get("/auth/me");
    return response.data;
  },

  // Logout
  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },

  // Send OTP
  sendOtp: async (data) => {
    const response = await api.post("/auth/send-otp", data);
    return response.data;
  },

  // Verify OTP
  verifyOtp: async (data) => {
    const response = await api.post("/auth/verify-otp", data);
    return response.data;
  },
};