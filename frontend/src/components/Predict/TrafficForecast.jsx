import React from "react";
import "./PredictComponents.css";

const InfoItem = ({ label, value }) => (
  <div className="info-item">
    <span className="info-item-label">{label.replace(/_/g, " ")}</span>
    <span className="info-item-value">{value}</span>
  </div>
);

const TrafficForecast = ({ forecast }) => {
  if (!forecast) return null;

  return (
    <div className="predict-card">
      <h3 className="card-title">Traffic Forecast</h3>
      <div className="card-content">
        <InfoItem label="Severity" value={forecast.severity} />
        <InfoItem label="Expected Delay" value={`${forecast.expected_delay_mins.toFixed(1)} mins`} />
      </div>
    </div>
  );
};

export default TrafficForecast;