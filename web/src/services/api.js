import axios from "axios";
const api=axios.create({baseURL:import.meta.env.VITE_API_BASE_URL||"http://127.0.0.1:8000",headers:{"Content-Type":"application/json"}});
api.interceptors.request.use((config)=>{const token=localStorage.getItem("fus_access_token");if(token) config.headers.Authorization=`Bearer ${token}`;return config;});
api.interceptors.response.use((r)=>r,(e)=>{if(e.response?.status===401){localStorage.removeItem("fus_access_token");localStorage.removeItem("fus_user");}return Promise.reject(e);});
export default api;
