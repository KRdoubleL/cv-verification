import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const login = async (email, password) => {
  const response = await api.post('/api/auth/login/json', { email, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/api/auth/me');
  return response.data;
};

// Candidates (Recruiter)
export const uploadCSV = async (file, batchName) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('batch_name', batchName);
  
  const response = await api.post('/api/candidates/upload/csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getBatches = async () => {
  const response = await api.get('/api/candidates/batches');
  return response.data;
};

export const getBatchDetail = async (batchId) => {
  const response = await api.get(`/api/candidates/batch/${batchId}`);
  return response.data;
};

export const getCandidate = async (candidateId) => {
  const response = await api.get(`/api/candidates/${candidateId}`);
  return response.data;
};

// Verification (Verifier)
export const getPendingCandidates = async () => {
  const response = await api.get('/api/verification/pending');
  return response.data;
};

export const claimCandidate = async (candidateId) => {
  const response = await api.post(`/api/verification/claim/${candidateId}`);
  return response.data;
};

export const getMyQueue = async () => {
  const response = await api.get('/api/verification/my-queue');
  return response.data;
};

export const updateEmployment = async (employmentId, data) => {
  const response = await api.put(`/api/verification/employment/${employmentId}`, data);
  return response.data;
};

export const updateEducation = async (educationId, data) => {
  const response = await api.put(`/api/verification/education/${educationId}`, data);
  return response.data;
};

export const completeVerification = async (candidateId) => {
  const response = await api.post(`/api/verification/complete/${candidateId}`);
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/api/verification/stats');
  return response.data;
};

// Reports
export const generateReport = async (candidateId) => {
  const response = await api.post(`/api/reports/generate/${candidateId}`);
  return response.data;
};

export const getReportUrl = (candidateId) => {
  const token = localStorage.getItem('token');
  return `${API_BASE_URL}/api/reports/candidate/${candidateId}/latest?token=${token}`;
};

export default api;