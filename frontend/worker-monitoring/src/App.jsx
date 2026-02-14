import React, { useState, useEffect } from 'react';
import '../src/App.css';
import {
  fetchFactoryMetrics,
  fetchWorkerMetrics,
  fetchWorkstationMetrics,
  seedData,
} from '../src/services/api';
import FactorySummary from '../src/components/FactorySummary';
import WorkerTable from '../src/components/WorkerTable';
import WorkstationTable from '../src/components/WorkStationTable';
import Filter from '../src/components/Filter';

function App() {
  const [factoryMetrics, setFactoryMetrics] = useState(null);
  const [workers, setWorkers] = useState([]);
  const [workstations, setWorkstations] = useState([]);
  const [filterType, setFilterType] = useState('none');
  const [filterValue, setFilterValue] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [factoryRes, workersRes, workstationsRes] = await Promise.all([
        fetchFactoryMetrics(),
        fetchWorkerMetrics(),
        fetchWorkstationMetrics(),
      ]);
      setFactoryMetrics(factoryRes.data);
      setWorkers(workersRes.data);
      setWorkstations(workstationsRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to load data. Make sure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSeed = async () => {
    try {
      await seedData();
      // Reload data after seeding (give background task a moment)
      setTimeout(loadData, 500);
    } catch (err) {
      setError('Failed to seed data.');
    }
  };

  const handleSelectWorker = (workerId) => {
    setFilterType('worker');
    setFilterValue(workerId);
  };

  const handleSelectStation = (stationId) => {
    setFilterType('workstation');
    setFilterValue(stationId);
  };

  if (loading) return <div className="app">Loading dashboard...</div>;
  if (error) return <div className="app error">{error}</div>;

  return (
    <div className="app">
      <h1>Worker Productivity Dashboard</h1>
      <button onClick={handleSeed} className="seed-btn">
        Regenerate Dummy Data
      </button>

      <Filter
        filterType={filterType}
        setFilterType={setFilterType}
        filterValue={filterValue}
        setFilterValue={setFilterValue}
        workers={workers}
        workstations={workstations}
      />

      <FactorySummary metrics={factoryMetrics} />

      <WorkerTable
        workers={workers}
        selectedWorker={filterType === 'worker' ? filterValue : null}
        onSelectWorker={handleSelectWorker}
      />

      <WorkstationTable
        workstations={workstations}
        selectedStation={filterType === 'workstation' ? filterValue : null}
        onSelectStation={handleSelectStation}
      />
    </div>
  );
}

export default App;