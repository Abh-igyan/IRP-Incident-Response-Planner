import React from "react";
import "./PredictComponents.css";

const MetricBand = ({
  impactScore,
  impactClass,
  closureProbability,
  confidenceScore,
  confidenceLabel,
}) => {
  const formattedConfidence = Number.isFinite(confidenceScore) ? Math.round(confidenceScore * 100) : null;
  return (
    <div className="predict-card metric-band">
      <div className="metric-item">
        <div className="metric-value">{impactScore.toFixed(2)}</div>
        <div className="metric-label">Impact Score</div>
      </div>
      <div className="metric-item">
        <div className="metric-sub-value">{impactClass}</div>
        <div className="metric-label">
          Impact Class {confidenceLabel ? `/ ${confidenceLabel}` : ""}
        </div>
      </div>
      <div className="metric-item">
        <div className="metric-value">
          {Math.round(closureProbability * 100)}
          <span className="unit">%</span>
        </div>
        <div className="metric-label">Closure Probability</div>
      </div>
      <div className="metric-item">
        <div className="metric-value">
          {formattedConfidence === null ? "-" : `${formattedConfidence}%`}
        </div>
        <div className="metric-label">Confidence Score</div>
      </div>
    </div>
  );
};

export default MetricBand;
