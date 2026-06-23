

import React, { useState, useEffect } from 'react';
import { Box, Grid, Paper, TextField, Button, Select, MenuItem, FormControl, InputLabel, Checkbox, FormControlLabel, CircularProgress, Typography } from '@mui/material';
import { getOptions, runPrediction, submitFeedback } from '../services/api';
import LocationPickerMap from '../components/Predict/LocationPickerMap';
import MetricBand from '../components/Predict/MetricBand';
import ResourcePlan from '../components/Predict/ResourcePlan';
import ResponsePlan from '../components/Predict/ResponsePlan';
import TrafficForecast from '../components/Predict/TrafficForecast';
import DiversionPlan from '../components/Predict/DiversionPlan';
import RouteMap from '../components/Predict/RouteMap';
import '../components/Predict/PredictComponents.css';

const PredictPage = () => {
  const [options, setOptions] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [feedbackState, setFeedbackState] = useState({
    actual_road_closure: false,
    actual_delay_mins: '',
    notes: '',
  });
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const context = predictionResult?.derived_context || null;
  const [formState, setFormState] = useState({
    event_type: '',
    event_cause: '',
    veh_type: '',
    priority: '',
    authenticated: true,
    latitude: 12.971599,
    longitude: 77.594566,
    incident_datetime: new Date().toISOString().slice(0, 16),
  });

  useEffect(() => {
    const loadOptions = async () => {
      try {
        const response = await getOptions();
        setOptions(response.data);
        setFormState((prev) => ({
          ...prev,
          event_type: response.data.event_type[0] || '',
          event_cause: response.data.event_cause[0] || '',
          veh_type: response.data.veh_type[0] || '',
          priority: response.data.priority[0] || '',
        }));
      } catch (error) {
        console.error('Failed to load options:', error);
        setError('Failed to load form options. Please try refreshing the page.');
      }
    };
    loadOptions();
  }, []);

  const handleChange = (event) => {
    const { name, value, checked, type } = event.target;
    setFormState((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleMapClick = (latlng) => {
    setFormState((prev) => ({
      ...prev,
      latitude: latlng[0],
      longitude: latlng[1],
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');
    setFeedbackMessage('');
    setPredictionResult(null);
    try {
      const response = await runPrediction(formState);
      setPredictionResult(response.data);
    } catch (error) {
      console.error('Prediction failed:', error);
      setError('Prediction request failed. Please check the inputs and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedbackChange = (event) => {
    const { name, value, checked, type } = event.target;
    setFeedbackState((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleFeedbackSubmit = async (event) => {
    event.preventDefault();
    if (!predictionResult) {
      setFeedbackMessage('Run a prediction before submitting feedback.');
      return;
    }

    try {
      await submitFeedback({
        incident: formState,
        prediction: predictionResult,
        actual_road_closure: feedbackState.actual_road_closure,
        actual_delay_mins: feedbackState.actual_delay_mins === '' ? null : Number(feedbackState.actual_delay_mins),
        notes: feedbackState.notes || null,
      });
      setFeedbackMessage('Feedback stored. The learning loop has been updated.');
      setFeedbackState({
        actual_road_closure: false,
        actual_delay_mins: '',
        notes: '',
      });
    } catch (feedbackError) {
      console.error('Feedback submission failed:', feedbackError);
      setFeedbackMessage('Unable to submit feedback right now.');
    }
  };

  if (!options) {
    return <p>Loading form...</p>;
  }

  return (
    <Grid container spacing={3} sx={{ p: 2 }}>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 2, backgroundColor: '#1a1d2e', color: '#e0e0e0' }}>
          <Typography variant="h6" sx={{ mb: 2, color: '#267cd9' }}>Create Incident Prediction</Typography>
          <Box component="form" onSubmit={handleSubmit} noValidate>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Event Type</InputLabel>
              <Select name="event_type" value={formState.event_type} onChange={handleChange}>
                {options.event_type.map((opt) => (<MenuItem key={opt} value={opt}>{opt}</MenuItem>))}
              </Select>
            </FormControl>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Event Cause</InputLabel>
              <Select name="event_cause" value={formState.event_cause} onChange={handleChange}>
                {options.event_cause.map((opt) => (<MenuItem key={opt} value={opt}>{opt}</MenuItem>))}
              </Select>
            </FormControl>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Vehicle Type</InputLabel>
              <Select name="veh_type" value={formState.veh_type} onChange={handleChange}>
                {options.veh_type.map((opt) => (<MenuItem key={opt} value={opt}>{opt}</MenuItem>))}
              </Select>
            </FormControl>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Priority</InputLabel>
              <Select name="priority" value={formState.priority} onChange={handleChange}>
                {options.priority.map((opt) => (<MenuItem key={opt} value={opt}>{opt}</MenuItem>))}
              </Select>
            </FormControl>
            <TextField
              name="latitude"
              label="Latitude"
              type="number"
              fullWidth
              value={formState.latitude}
              onChange={handleChange}
              sx={{ mb: 2 }}
            />
            <TextField
              name="longitude"
              label="Longitude"
              type="number"
              fullWidth
              value={formState.longitude}
              onChange={handleChange}
              sx={{ mb: 2 }}
            />
            <TextField
              name="incident_datetime"
              label="Incident Datetime"
              type="datetime-local"
              fullWidth
              value={formState.incident_datetime}
              onChange={handleChange}
              InputLabelProps={{ shrink: true }}
              sx={{ mb: 2 }}
            />
            <FormControlLabel
              control={<Checkbox name="authenticated" checked={formState.authenticated} onChange={handleChange} />}
              label="Authenticated"
              sx={{ mb: 2 }}
            />
            <Button type="submit" variant="contained" fullWidth disabled={isLoading}>
              {isLoading ? <CircularProgress size={24} /> : 'Run Prediction'}
            </Button>
          </Box>
        </Paper>
        <Paper sx={{ mt: 2, p: 2, backgroundColor: '#1a1d2e', color: '#e0e0e0' }}>
          <Typography variant="subtitle2" sx={{ mb: 1, color: '#a0a0a0' }}>
            Operational Context
          </Typography>
          <Box sx={{ display: 'grid', gap: 0.75, fontSize: '0.92rem', color: '#cfd8dc' }}>
            <span>Corridor: {context?.corridor || '-'}</span>
            <span>Zone: {context?.zone || '-'}</span>
            <span>Station: {context?.police_station || '-'}</span>
            <span>Time: {context ? `${context.hour}:00 ${context.is_peak_hour ? '(Peak)' : '(Off-peak)'}` : '-'}</span>
          </Box>
        </Paper>
      </Grid>
      <Grid item xs={12} md={8}>
        {isLoading && <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 240 }}><CircularProgress /></Box>}
        {error && <Typography color="error">{error}</Typography>}
        <Box sx={{ display: 'grid', gap: 2, gridTemplateRows: '360px 360px' }}>
          <Paper sx={{ height: 360, backgroundColor: '#1a1d2e', overflow: 'hidden' }}>
            <Box sx={{ px: 2, pt: 2 }}>
              <Typography variant="h6" sx={{ color: '#e0e0e0' }}>
                Incident Location
              </Typography>
            </Box>
            <Box sx={{ height: 'calc(100% - 58px)' }}>
              <LocationPickerMap
                position={[formState.latitude, formState.longitude]}
                onPositionChange={handleMapClick}
              />
            </Box>
          </Paper>

          <Paper sx={{ height: 360, backgroundColor: '#1a1d2e', overflow: 'hidden' }}>
            <Box sx={{ px: 2, pt: 2 }}>
              <Typography variant="h6" sx={{ color: '#e0e0e0' }}>
                Diversion Route
              </Typography>
            </Box>
            <Box sx={{ height: 'calc(100% - 58px)' }}>
              <RouteMap
                incidentPosition={[formState.latitude, formState.longitude]}
                routeCoords={predictionResult?.diversion_plan?.route_coords || []}
              />
            </Box>
          </Paper>
        </Box>

        {predictionResult && (
          <>
            <div className="predict-grid" style={{padding: 0, gridTemplateColumns: '1fr' }}>
                <MetricBand
                  impactScore={predictionResult.impact_score}
                  impactClass={predictionResult.impact_class}
                  closureProbability={predictionResult.closure_probability}
                  confidenceScore={predictionResult.prediction_confidence?.score}
                  confidenceLabel={predictionResult.prediction_confidence?.label}
                />
            </div>
            <div className="predict-grid" style={{padding: '1.5rem 0 0 0'}}>
                <ResourcePlan plan={predictionResult.resource_plan} />
                <ResponsePlan
                  priority={predictionResult.response_priority}
                  eta={predictionResult.eta_target}
                />
                <TrafficForecast forecast={predictionResult.traffic_forecast} />
                <DiversionPlan
                  strategy={predictionResult.diversion_strategy}
                  plan={predictionResult.diversion_plan}
                />
            </div>
          </>
        )}
        <Paper sx={{ mt: 2, p: 2, backgroundColor: '#1a1d2e', color: '#e0e0e0' }}>
          <Typography variant="h6" sx={{ mb: 2, color: '#267cd9' }}>
            Post-Event Feedback
          </Typography>
          <Box component="form" onSubmit={handleFeedbackSubmit} noValidate>
            <FormControlLabel
              control={
                <Checkbox
                  name="actual_road_closure"
                  checked={feedbackState.actual_road_closure}
                  onChange={handleFeedbackChange}
                />
              }
              label="Road closure happened"
              sx={{ mb: 1 }}
            />
            <TextField
              name="actual_delay_mins"
              label="Actual Delay (mins)"
              type="number"
              fullWidth
              value={feedbackState.actual_delay_mins}
              onChange={handleFeedbackChange}
              sx={{ mb: 2 }}
            />
            <TextField
              name="notes"
              label="Operator Notes"
              fullWidth
              multiline
              minRows={3}
              value={feedbackState.notes}
              onChange={handleFeedbackChange}
              sx={{ mb: 2 }}
            />
            <Button type="submit" variant="outlined" fullWidth disabled={!predictionResult || isLoading}>
              Submit Feedback
            </Button>
            {feedbackMessage && (
              <Typography sx={{ mt: 1.5, color: '#a0a0a0' }}>
                {feedbackMessage}
              </Typography>
            )}
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default PredictPage;
