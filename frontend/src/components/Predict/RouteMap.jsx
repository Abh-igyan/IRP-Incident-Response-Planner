import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Icon fix for Vite/Esm builds.
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const FitBounds = ({ bounds }) => {
    const map = useMap();
    useEffect(() => {
        if (bounds.isValid()) {
            map.fitBounds(bounds);
        }
    }, [map, bounds]);
    return null;
}

const RouteMap = ({ incidentPosition, routeCoords }) => {
  const bounds = L.latLngBounds(routeCoords && routeCoords.length > 0 ? routeCoords : [incidentPosition]).pad(0.1);

  return (
    <MapContainer bounds={bounds} style={{ height: '100%', width: '100%' }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap contributors' />
      <Marker position={incidentPosition} />
      {routeCoords && routeCoords.length > 1 && <Polyline positions={routeCoords} color="#267cd9" weight={5} />}
      <FitBounds bounds={bounds} />
    </MapContainer>
  );
};

export default RouteMap;
