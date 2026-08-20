import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post('/api/auth/refresh/', {
            refresh: refreshToken
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (credentials) => api.post('/api/auth/login/', credentials),
  register: (userData) => api.post('/api/auth/register/', userData),
  getProfile: () => api.get('/api/auth/profile/'),
};

export const projectAPI = {
  list: () => api.get('/api/projects/'),
  create: (data) => api.post('/api/projects/', data),
  get: (id) => api.get(`/api/projects/${id}/`),
  update: (id, data) => api.put(`/api/projects/${id}/`, data),
  delete: (id) => api.delete(`/api/projects/${id}/`),
  addMember: (id, userId) => api.post(`/api/projects/${id}/add_member/`, { user_id: userId }),
  removeMember: (id, userId) => api.post(`/api/projects/${id}/remove_member/`, { user_id: userId }),
  getStatistics: (id) => api.get(`/api/projects/${id}/statistics/`),
};

export const taskAPI = {
  list: (params) => api.get('/api/tasks/', { params }),
  create: (data) => api.post('/api/tasks/', data),
  get: (id) => api.get(`/api/tasks/${id}/`),
  update: (id, data) => api.put(`/api/tasks/${id}/`, data),
  delete: (id) => api.delete(`/api/tasks/${id}/`),
  updateStatus: (id, status) => api.patch(`/api/tasks/${id}/update_status/`, { status }),
  updatePriority: (id, priority) => api.patch(`/api/tasks/${id}/update_priority/`, { priority }),
};

export const commentAPI = {
  list: (taskId) => api.get(`/api/tasks/${taskId}/comments/`),
  create: (taskId, data) => api.post(`/api/tasks/${taskId}/comments/`, data),
  update: (taskId, commentId, data) => api.put(`/api/tasks/${taskId}/comments/${commentId}/`, data),
  delete: (taskId, commentId) => api.delete(`/api/tasks/${taskId}/comments/${commentId}/`),
};

export const userAPI = {
  list: (params) => api.get('/api/users/', { params }),
};

export default api;
