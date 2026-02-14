import React from 'react';

const WorkstationTable = ({ workstations, selectedStation, onSelectStation }) => {
  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hrs}h ${mins}m`;
  };

  return (
    <div className="workstation-table">
      <h2>Workstations</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Occupancy Time</th>
            <th>Utilization</th>
            <th>Units Produced</th>
            <th>Throughput (units/hr)</th>
          </tr>
        </thead>
        <tbody>
          {workstations.map((station) => (
            <tr
              key={station.station_id}
              className={selectedStation === station.station_id ? 'selected' : ''}
              onClick={() => onSelectStation(station.station_id)}
            >
              <td>{station.station_id}</td>
              <td>{station.name}</td>
              <td>{formatTime(station.occupancy_time)}</td>
              <td>{station.utilization_percentage.toFixed(1)}%</td>
              <td>{station.total_units_produced}</td>
              <td>{station.throughput_rate.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default WorkstationTable;