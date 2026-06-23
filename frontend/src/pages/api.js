import axios from 'axios';

// In development, the React app will be proxied to the FastAPI backend.
// This assumes the backend runs on http://127.0.0.1:8000 as per the README.
const API_BASE_URL = '/';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetches the dropdown options for the prediction form.
 * Corresponds to the GET /options endpoint.
 */
export const getOptions = () => {
  return apiClient.get('options');
};

/**
 * Submits the incident data to get a prediction.
 * Corresponds to the POST /predict endpoint.
 * @param {object} incidentData - The data from the prediction form.
 */
export const runPrediction = (incidentData) => {
  return apiClient.post('predict', incidentData);
};

/**
 * Fetches the feedback summary for the analytics dashboard.
 * Corresponds to the GET /feedback/summary endpoint.
 */
export const getFeedbackSummary = () => {
    return apiClient.get('feedback/summary');
};