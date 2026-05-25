import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001/api/v1",
  timeout: 20000
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const msg = err?.response?.data?.detail || err?.message || "Network error";
    return Promise.reject(new Error(msg));
  }
);

export const marketApi = {
  predict: async (payload) => (await api.post("/market/predict", payload)).data,
  crops: async () => (await api.get("/market/crops")).data,
  mandis: async () => (await api.get("/market/mandis")).data
};

export const pestApi = {
  checkRisk: async (payload) => (await api.post("/pest/check-risk", payload)).data
};

export const cropApi = {
  recommend: async (payload) => (await api.post("/crop/recommend", payload)).data
};

export const supportApi = {
  createTicket: async (formData) =>
    (
      await api.post("/support/create-ticket", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      })
    ).data,
  faqs: async () => (await api.get("/support/faqs")).data
};

