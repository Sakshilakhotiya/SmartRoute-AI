import axios from 'axios';
export const api=axios.create({baseURL:import.meta.env.VITE_API_URL||'http://localhost:5000/api'});
api.interceptors.request.use(c=>{const t=localStorage.getItem('sr_token');if(t)c.headers.Authorization=`Bearer ${t}`;return c;});
export function setToken(t:string|null){if(t)localStorage.setItem('sr_token',t);else localStorage.removeItem('sr_token');}
