import axios from "axios";

const api = axios.create({
  baseURL: "https://cartsy-ht0x.onrender.com/api/",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
