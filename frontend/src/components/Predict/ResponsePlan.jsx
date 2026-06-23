import React from "react";
import "./PredictComponents.css";

const InfoItem = ({ label, value }) => (
  <div className="info-item">
    <span className="info-item-label">{label.replace(/_/g, " ")}</span>
    <span className="info-item-value">{value}</span>
  </div>
);

const ResponsePlan = ({ priority, eta }) => {
  return (
    <div className="predict-card">
      <h3 className="card-title">Response Plan</h3>
      <div className="card-content">
        <InfoItem label="Response Priority" value={priority} />
        <InfoItem label="ETA Target" value={eta} />
      </div>
    </div>
  );
};

export default ResponsePlan;