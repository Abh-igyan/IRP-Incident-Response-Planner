import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix for the default Leaflet icon resolution under Vite/Esm builds.
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const MapEventsHandler = ({ onPositionChange }) => {
  useMapEvents({
    click(e) {
      onPositionChange([e.latlng.lat, e.latlng.lng]);
    },
  });
  return null;
};

const MapPositionUpdater = ({ position }) => {
    const map = useMap();
    useEffect(() => {
        map.setView(position, map.getZoom());
    }, [position, map]);
    return null;
}

const LocationPickerMap = ({ position, onPositionChange }) => {
  return (
    <MapContainer center={position} zoom={12} style={{ height: '100%', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <Marker position={position}></Marker>
      <MapEventsHandler onPositionChange={onPositionChange} />
      <MapPositionUpdater position={position} />
    </MapContainer>
  );
};

export default LocationPickerMap;
