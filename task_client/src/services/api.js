import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (email, password, name) => {
    const response = await api.post('/auth/register', { email, password, name });
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
};

// Projects API
export const projectsAPI = {
  getAll: async () => {
    const response = await api.get('/projects');
    return response.data;
  },

  create: async (name, description) => {
    const response = await api.post('/projects', { name, description });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },
};

// Tasks API
export const tasksAPI = {
  getByProject: async (projectId) => {
    const response = await api.get(`/tasks/projects/${projectId}/tasks`);
    return response.data;
  },

  create: async (taskData) => {
    const response = await api.post('/tasks', taskData);
    return response.data;
  },

  update: async (taskId, updates) => {
    const response = await api.patch(`/tasks/${taskId}`, updates);
    return response.data;
  },

  delete: async (taskId) => {
    const response = await api.delete(`/tasks/${taskId}`);
    return response.data;
  },
};

// Users API
export const usersAPI = {
  getAll: async () => {
    const response = await api.get('/users');
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/users/stats');
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },
};

// Reports API
export const reportsAPI = {
  getDailySummary: async (projectId, options = {}) => {
    const response = await api.post('/reports/daily_summary', {
      project_id: projectId,
      include_overdue: options.include_overdue ?? true,
      include_assignees: options.include_assignees ?? true,
      compact: options.compact ?? false,
    });
    return response.data;
  },

  getProjectReport: async (projectId) => {
    const response = await api.get(`/reports/project/${projectId}`);
    return response.data;
  },

  getOverdueReport: async () => {
    const response = await api.get('/reports/overdue');
    return response.data;
  },
};

export default api;
