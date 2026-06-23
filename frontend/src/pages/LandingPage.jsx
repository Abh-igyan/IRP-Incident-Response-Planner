
import React from 'react';
import { Box, Typography, Button, Grid, Paper, Chip } from '@mui/material';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  const archNodes = [
    'Incident Input',
    'Feature Context',
    'CatBoost + Calibration',
    'Rules + Feedback',
    'Response Plan',
  ];

  const capabilities = [
    {
      title: 'ML Pipeline',
      description: 'CatBoost produces the raw closure score, then confidence scoring, calibration, rule checks, and feedback profiles stabilize the final probability.',
    },
    {
      title: 'Routing Pipeline',
      description: 'Incident coordinates select the nearest graph candidates directly, so diversion planning does not collapse when corridor labels are missing.',
    },
    {
      title: 'Operational Outputs',
      description: 'The dashboard returns impact score, confidence score, priority, ETA target, officers, barricades, vehicles, emergency flags, route details, and post-event feedback capture.',
    },
    {
      title: 'Feedback Learning',
      description: 'Post-event closure and delay outcomes update learned profiles that tune future estimates while preserving the stable model baseline.',
    },
    {
      title: 'Analytics and Heatmap',
      description: 'Operational analytics include downloadable exports, corridor plots, hourly charts, and a true Leaflet heatmap view.',
    },
  ];

  return (
    <Box sx={{ p: 4 }}>
      {/* Hero Section */}
      <Box sx={{ textAlign: 'center', mb: 8 }}>
        <Typography variant="h6" color="primary" gutterBottom>
          Incident Response Planner
        </Typography>
        <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Traffic Intelligence for Bengaluru
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ mb: 4 }}>
          Forecast closure risk, estimate operational impact, plan resources, and route diversions with a hybrid ML, rules, and graph-routing pipeline.
        </Typography>
        <Button
          variant="contained"
          size="large"
          component={Link}
          to="/predict"
        >
          Open Operations Console
        </Button>
      </Box>

      {/* Architecture Section */}
      <Box sx={{ mb: 8 }}>
        <Typography variant="h4" component="h2" sx={{ textAlign: 'center', mb: 4 }}>
          System Architecture
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap', gap: 2 }}>
          {archNodes.map((node, index) => (
            <React.Fragment key={node}>
              <Chip label={node} />
              {index < archNodes.length - 1 && <Box component="span" sx={{ color: 'primary.main', fontSize: 24 }}>→</Box>}
            </React.Fragment>
          ))}
        </Box>
        <Chip label="Nearest Graph Routing + Optional Mappls Validation" sx={{ display: 'block', mx: 'auto', mt: 2 }}/>
      </Box>

      {/* Capabilities Section */}
      <Box>
        <Typography variant="h4" component="h2" sx={{ textAlign: 'center', mb: 4 }}>
          Key Capabilities
        </Typography>
        <Grid container spacing={4}>
          {capabilities.map((item) => (
            <Grid item xs={12} md={6} key={item.title}>
              <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h5" component="h3" gutterBottom>
                  {item.title}
                </Typography>
                <Typography color="text.secondary">{item.description}</Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  );
};

export default LandingPage;
