import React from 'react';

const WorkerTable = ({ workers, selectedWorker, onSelectWorker }) => {
  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hrs}h ${mins}m`;
  };

  return (
    <div className="worker-table">
      <h2>Workers</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Active Time</th>
            <th>Idle Time</th>
            <th>Utilization</th>
            <th>Units Produced</th>
            <th>Units/hr</th>
          </tr>
        </thead>
        <tbody>
          {workers.map((worker) => (
            <tr
              key={worker.worker_id}
              className={selectedWorker === worker.worker_id ? 'selected' : ''}
              onClick={() => onSelectWorker(worker.worker_id)}
            >
              <td>{worker.worker_id}</td>
              <td>{worker.name}</td>
              <td>{formatTime(worker.total_active_time)}</td>
              <td>{formatTime(worker.total_idle_time)}</td>
              <td>{worker.utilization_percentage.toFixed(1)}%</td>
              <td>{worker.total_units_produced}</td>
              <td>{worker.units_per_hour.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default WorkerTable;