import React from 'react';

const Filter = ({ filterType, setFilterType, filterValue, setFilterValue, workers, workstations }) => {
  const handleTypeChange = (e) => {
    setFilterType(e.target.value);
    setFilterValue(''); // reset selected value when type changes
  };

  return (
    <div className="filter">
      <label>
        Filter by:
        <select value={filterType} onChange={handleTypeChange}>
          <option value="none">None</option>
          <option value="worker">Worker</option>
          <option value="workstation">Workstation</option>
        </select>
      </label>

      {filterType === 'worker' && (
        <label>
          Select Worker:
          <select value={filterValue} onChange={(e) => setFilterValue(e.target.value)}>
            <option value="">-- Choose --</option>
            {workers.map((w) => (
              <option key={w.worker_id} value={w.worker_id}>
                {w.worker_id} - {w.name}
              </option>
            ))}
          </select>
        </label>
      )}

      {filterType === 'workstation' && (
        <label>
          Select Workstation:
          <select value={filterValue} onChange={(e) => setFilterValue(e.target.value)}>
            <option value="">-- Choose --</option>
            {workstations.map((ws) => (
              <option key={ws.station_id} value={ws.station_id}>
                {ws.station_id} - {ws.name}
              </option>
            ))}
          </select>
        </label>
      )}
    </div>
  );
};

export default Filter;