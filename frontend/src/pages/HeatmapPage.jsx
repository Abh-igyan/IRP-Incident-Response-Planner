import React, { useEffect, useMemo, useState } from 'react';
import { Box, CircularProgress, Divider, Paper, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { CircleMarker, MapContainer, TileLayer, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getHeatmapData } from '../services/api';

const defaultCenter = [12.971599, 77.594566];

const incidentPalette = {
  accident: '#ff4d4d',
  fire: '#ff006e',
  protest: '#a855f7',
  public_event: '#8b5cf6',
  construction: '#f59e0b',
  roadwork: '#f97316',
  vehicle_breakdown: '#14b8a6',
  tree_fall: '#22c55e',
  debris: '#06b6d4',
  procession: '#ec4899',
  default: '#60a5fa',
};

const normalizeKey = (value) => String(value || '').trim().toLowerCase().replace(/\s+/g, '_');

const getIncidentColor = (record) => {
  const key = normalizeKey(record?.incident_category || record?.event_cause || record?.event_type);
  if (incidentPalette[key]) return incidentPalette[key];
  if (key.includes('accident')) return incidentPalette.accident;
  if (key.includes('fire')) return incidentPalette.fire;
  if (key.includes('protest')) return incidentPalette.protest;
  if (key.includes('event')) return incidentPalette.public_event;
  if (key.includes('construct')) return incidentPalette.construction;
  if (key.includes('breakdown')) return incidentPalette.vehicle_breakdown;
  if (key.includes('tree')) return incidentPalette.tree_fall;
  if (key.includes('debris')) return incidentPalette.debris;
  if (key.includes('process')) return incidentPalette.procession;
  return incidentPalette.default;
};

const getLabel = (record) => record?.incident_category || record?.event_cause || record?.event_type || 'unknown';

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
  const bounds = useMemo(() => {
    const coords = topRows
      .map((record) => [Number(record.latitude), Number(record.longitude)])
      .filter(([lat, lon]) => Number.isFinite(lat) && Number.isFinite(lon));
    return coords.length >= 2 ? coords : null;
  }, [topRows]);
  const legendItems = useMemo(() => {
    const seen = new Map();
    (data || []).forEach((record) => {
      const label = getLabel(record);
      const key = normalizeKey(label);
      if (!seen.has(key)) {
        seen.set(key, { label, color: getIncidentColor(record) });
      }
    });
    return Array.from(seen.values()).slice(0, 8);
  }, [data]);

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
          Incident type heatmap
        </Typography>
        <Typography sx={{ color: '#a0a0a0', mb: 2 }}>
          Each marker is colored by incident category. Size still reflects operational severity so the map stays useful for scanning.
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, mb: 2 }}>
          {legendItems.map((item) => (
            <Box key={item.label} sx={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: item.color, border: '1px solid rgba(255,255,255,0.4)' }} />
              <Typography variant="body2" sx={{ color: '#d7d7d7' }}>
                {item.label}
              </Typography>
            </Box>
          ))}
        </Box>
        <Box sx={{ height: 520, borderRadius: 1, overflow: 'hidden' }}>
          <MapContainer center={defaultCenter} bounds={bounds || undefined} zoom={11} style={{ height: '100%', width: '100%' }}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; OpenStreetMap contributors'
            />
            {topRows.map((record, index) => {
              const lat = Number(record.latitude);
              const lon = Number(record.longitude);
              const intensity = Number(record.intensity ?? 0.5) || 0.5;
              const color = getIncidentColor(record);
              const label = getLabel(record);
              return (
                <CircleMarker
                  key={`${lat}-${lon}-${index}`}
                  center={[lat, lon]}
                  radius={9 + intensity * 10}
                  pathOptions={{
                    color,
                    fillColor: color,
                    fillOpacity: 0.58,
                    weight: 1.5,
                  }}
                >
                  <Tooltip>
                    <Box component="span">
                      {label}
                      {' '}
                      at {lat.toFixed(5)}, {lon.toFixed(5)}
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
          Sample incident markers
        </Typography>
        <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)', mb: 2 }} />
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: '#a0a0a0' }}>Latitude</TableCell>
              <TableCell sx={{ color: '#a0a0a0' }}>Longitude</TableCell>
              <TableCell sx={{ color: '#a0a0a0' }}>Incident Type</TableCell>
              <TableCell sx={{ color: '#a0a0a0' }}>Cause</TableCell>
              <TableCell sx={{ color: '#a0a0a0' }}>Color</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {topRows.slice(0, 12).map((record, index) => (
              <TableRow key={`${record.latitude}-${record.longitude}-${index}`}>
                <TableCell sx={{ color: '#e0e0e0' }}>{Number(record.latitude).toFixed(5)}</TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>{Number(record.longitude).toFixed(5)}</TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>{getLabel(record)}</TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>{record.event_cause || '-'}</TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>
                  <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: getIncidentColor(record), border: '1px solid rgba(255,255,255,0.35)' }} />
                    {getIncidentColor(record)}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
};

export default HeatmapPage;
