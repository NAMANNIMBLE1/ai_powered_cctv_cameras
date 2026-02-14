import React from 'react';

const FactorySummary = ({ metrics }) => {
  if (!metrics) return <div>Loading factory metrics...</div>;

  // Format seconds to hours:minutes
  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hrs}h ${mins}m`;
  };

  return (
    <div className="factory-summary">
      <h2>Factory Summary</h2>
      <div className="summary-cards">
        <div className="card">
          <h3>Total Productive Time</h3>
          <p>{formatTime(metrics.total_productive_time)}</p>
        </div>
        <div className="card">
          <h3>Total Production</h3>
          <p>{metrics.total_production_count} units</p>
        </div>
        <div className="card">
          <h3>Avg Production Rate</h3>
          <p>{metrics.avg_production_rate.toFixed(2)} units/hr</p>
        </div>
        <div className="card">
          <h3>Avg Utilization</h3>
          <p>{metrics.avg_utilization.toFixed(1)}%</p>
        </div>
      </div>
    </div>
  );
};

export default FactorySummary;