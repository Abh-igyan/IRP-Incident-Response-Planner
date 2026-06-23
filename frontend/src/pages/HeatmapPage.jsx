import React, { useEffect, useMemo, useState } from 'react';
import { Box, CircularProgress, Paper, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { CircleMarker, MapContainer, TileLayer, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getHeatmapData } from '../services/api';

const defaultCenter = [12.971599, 77.594566];

const getHeatColor = (intensity) => {
  if (intensity >= 0.85) return '#ff4d4d';
  if (intensity >= 0.65) return '#ff8c42';
  if (intensity >= 0.45) return '#ffd166';
  return '#4cc9f0';
};

const HeatmapPage = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    getHeatmapData()
      .then((response) => {
        if (mounted) setData(response.data.heatmap || []);
      })
      .catch((err) => {
        console.error('Failed to load heatmap:', err);
        if (mounted) setError('Unable to load heatmap data from the backend.');
      });
    return () => {
      mounted = false;
    };
  }, []);

  const topRows = useMemo(() => (data || []).slice(0, 200), [data]);

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  if (!data) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 240 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'grid', gap: 3 }}>
      <Typography variant="h4" sx={{ color: '#e0e0e0' }}>
        Heatmap
      </Typography>

      <Paper sx={{ p: 2, backgroundColor: '#1a1d2e', color: '#e0e0e0' }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Incident intensity heatmap
        </Typography>
        <Box sx={{ height: 520, borderRadius: 1, overflow: 'hidden' }}>
          <MapContainer center={defaultCenter} zoom={11} style={{ height: '100%', width: '100%' }}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; OpenStreetMap contributors'
            />
            {topRows.map(([lat, lon, intensity], index) => {
              const safeIntensity = Number(intensity) || 0;
              const color = getHeatColor(safeIntensity);
              return (
                <CircleMarker
                  key={`${lat}-${lon}-${index}`}
                  center={[Number(lat), Number(lon)]}
                  radius={10 + safeIntensity * 18}
                  pathOptions={{
                    color,
                    fillColor: color,
                    fillOpacity: 0.38 + safeIntensity * 0.3,
                    weight: 1,
                  }}
                >
                  <Tooltip>
                    <Box component="span">
                      {Number(lat).toFixed(5)}, {Number(lon).toFixed(5)}
                      {' '}
                      ({safeIntensity.toFixed(2)})
                    </Box>
                  </Tooltip>
                </CircleMarker>
              );
            })}
          </MapContainer>
        </Box>
      </Paper>

      <Paper sx={{ p: 2, backgroundColor: '#1a1d2e', color: '#e0e0e0' }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Backend heatmap points
        </Typography>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: '#a0a0a0' }}>Latitude</TableCell>
              <TableCell sx={{ color: '#a0a0a0' }}>Longitude</TableCell>
              <TableCell sx={{ color: '#a0a0a0' }}>Intensity</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {topRows.slice(0, 12).map(([lat, lon, intensity], index) => (
              <TableRow key={`${lat}-${lon}-${index}`}>
                <TableCell sx={{ color: '#e0e0e0' }}>{Number(lat).toFixed(5)}</TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>{Number(lon).toFixed(5)}</TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>{Number(intensity).toFixed(2)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
};

export default HeatmapPage;
