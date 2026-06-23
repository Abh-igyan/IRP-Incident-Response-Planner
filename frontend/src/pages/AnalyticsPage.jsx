import React, { useEffect } from 'react';
import { Box, CircularProgress, Paper, Typography } from '@mui/material';

const STATIC_ANALYTICS_URL = '/analytics/index.html';

const AnalyticsPage = () => {
  useEffect(() => {
    window.location.replace(STATIC_ANALYTICS_URL);
  }, []);

  return (
    <Paper sx={{ p: 3, backgroundColor: '#1a1d2e', color: '#e0e0e0', minHeight: 240, display: 'grid', placeItems: 'center' }}>
      <Box sx={{ textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2, color: '#a0a0a0' }}>
          Redirecting to the static analytics dashboard...
        </Typography>
      </Box>
    </Paper>
  );
};

export default AnalyticsPage;
