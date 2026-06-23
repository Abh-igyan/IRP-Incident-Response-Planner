
import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';

const Map = ({ center, zoom, markerPosition, onMapClick, routeCoords }) => {
  return (
    <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%' }} onClick={onMapClick}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {markerPosition && <Marker position={markerPosition}>
        <Popup>Incident Location</Popup>
      </Marker>}
      {routeCoords && <Polyline positions={routeCoords} color="blue" />}
    </MapContainer>
  );
};

export default Map;
