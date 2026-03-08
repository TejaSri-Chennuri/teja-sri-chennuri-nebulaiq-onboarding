import { create } from 'zustand';
import { authAPI } from '../services/api';

const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem('zentra_user') || 'null'),
  token: localStorage.getItem('zentra_token') || null,
  isAuthenticated: !!localStorage.getItem('zentra_token'),
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.login(email, password);
      const { access_token, user } = response.data;
      localStorage.setItem('zentra_token', access_token);
      localStorage.setItem('zentra_user', JSON.stringify(user));
      set({ user, token: access_token, isAuthenticated: true, loading: false });
      return { success: true };
    } catch (error) {
      const msg = error.response?.data?.detail || 'Login failed';
      set({ error: msg, loading: false });
      return { success: false, error: msg };
    }
  },

  register: async (data) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.register(data);
      const { access_token, user } = response.data;
      localStorage.setItem('zentra_token', access_token);
      localStorage.setItem('zentra_user', JSON.stringify(user));
      set({ user, token: access_token, isAuthenticated: true, loading: false });
      return { success: true };
    } catch (error) {
      const msg = error.response?.data?.detail || 'Registration failed';
      set({ error: msg, loading: false });
      return { success: false, error: msg };
    }
  },

  logout: () => {
    localStorage.removeItem('zentra_token');
    localStorage.removeItem('zentra_user');
    set({ user: null, token: null, isAuthenticated: false });
  },

  updateUser: (user) => {
    localStorage.setItem('zentra_user', JSON.stringify(user));
    set({ user });
  },
}));

export default useAuthStore;
