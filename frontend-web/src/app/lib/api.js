import axios from "axios";

const api = axios.create({
  baseURL: "https://cartsy-ht0x.onrender.com/api/",
  withCredentials: true,
});

export default api;
