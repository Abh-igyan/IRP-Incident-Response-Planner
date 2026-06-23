import React from "react";
import "./PredictComponents.css";

const InfoItem = ({ label, value }) => {
  const displayValue = typeof value === "boolean" ? (value ? "Yes" : "No") : value;
  const valueClass =
    typeof value === "boolean"
      ? `boolean-${value.toString()}`
      : "";

  return (
    <div className="info-item">
      <span className="info-item-label">{label.replace(/_/g, " ")}</span>
      <span className={`info-item-value ${valueClass}`}>{displayValue}</span>
    </div>
  );
};

const ResourcePlan = ({ plan }) => {
  if (!plan) return null;

  return (
    <div className="predict-card">
      <h3 className="card-title">Resource Plan</h3>
      <div className="card-content">
        <InfoItem label="Officers" value={plan.officers} />
        <InfoItem label="Barricades" value={plan.barricades} />
        <InfoItem label="Patrol Vehicles" value={plan.patrol_vehicles} />
        <InfoItem label="Ambulance Required" value={plan.ambulance_required} />
        <InfoItem label="Crane Required" value={plan.crane_required} />
      </div>
    </div>
  );
};

export default ResourcePlan;