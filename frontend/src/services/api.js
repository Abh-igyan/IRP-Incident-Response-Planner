
import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/', // Assuming the frontend is served from the same domain as the backend
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getOptions = () => {
  return apiClient.get('/options');
};

export const runPrediction = (payload) => {
  return apiClient.post('/predict', payload);
};

export const submitFeedback = (payload) => {
  return apiClient.post('/feedback', payload);
};

export const getAnalyticsBundle = () => {
  return apiClient.get('/analytics');
};

export const getHeatmapData = () => {
  return apiClient.get('/analytics/heatmap');
};

export const getFeedbackSummary = () => {
  return apiClient.get('/feedback/summary');
};
