import React from "react";
import "./PredictComponents.css";

const InfoItem = ({ label, value, children }) => (
  <div className="info-item">
    <span className="info-item-label">{label.replace(/_/g, " ")}</span>
    {children || <span className="info-item-value">{value}</span>}
  </div>
);

const DiversionPlan = ({ strategy, plan }) => {
  if (!plan) return null;

  const distance = plan.best_diversion_distance_km;
  const eta = plan.best_diversion_eta_mins;
  const roads = plan.alternate_roads || [];

  return (
    <div className="predict-card">
      <h3 className="card-title">Diversion Plan</h3>
      <div className="card-content">
        <InfoItem label="Strategy" value={strategy} />
        <InfoItem
          label="Best Diversion Distance"
          value={distance ? `${distance.toFixed(2)} km` : "-"}
        />
        <InfoItem
          label="Best Diversion ETA"
          value={eta ? `${eta.toFixed(1)} mins` : "-"}
        />
        <InfoItem label="Diversion Road" value={plan.diversion_road_name || "-"} />
        <InfoItem label="Alternate Roads">
          {roads.length > 0 ? (
            <ul className="alternate-roads-list">
              {roads.map((road, index) => (
                <li key={index}>{road}</li>
              ))}
            </ul>
          ) : (
            <span className="info-item-value">-</span>
          )}
        </InfoItem>
      </div>
    </div>
  );
};

export default DiversionPlan;