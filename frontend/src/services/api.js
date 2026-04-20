import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const login = async (email, password) => {
  const response = await api.post('/api/auth/login/json', { email, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/api/auth/me');
  return response.data;
};

export const uploadPDF = async (file, batchName) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('batch_name', batchName);
  const response = await api.post('/api/candidates/upload/pdf', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

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

export const deleteCandidate = async (candidateId) => {
  const response = await api.delete(`/api/candidates/${candidateId}`);
  return response.data;
};

// Verification
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

export const getSectionChecks = async (candidateId) => {
  const response = await api.get(`/api/verification/sections/${candidateId}`);
  return response.data;
};

export const markSectionChecked = async (candidateId, sectionType, sectionRefId, note) => {
  const response = await api.post(`/api/verification/sections/${candidateId}/check`, {
    section_type: sectionType,
    section_ref_id: sectionRefId,
    note
  });
  return response.data;
};

export const markSectionChanged = async (candidateId, sectionType, sectionRefId, oldValue, newValue, note) => {
  const response = await api.post(`/api/verification/sections/${candidateId}/change`, {
    section_type: sectionType,
    section_ref_id: sectionRefId,
    old_value: oldValue,
    new_value: newValue,
    note
  });
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

export const generateReport = async (candidateId) => {
  const response = await api.post(`/api/reports/generate/${candidateId}`);
  return response.data;
};

export const getReportUrl = (candidateId) => {
  const token = localStorage.getItem('token');
  return `${API_BASE_URL}/api/reports/candidate/${candidateId}/latest?token=${token}`;
};

export default api;