from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .models import EventType


class EventCreate(BaseModel):
    timestamp: datetime
    worker_id: str
    workstation_id: str
    event_type: EventType
    confidence: Optional[float] = None
    count: Optional[int] = None


class WorkerMetrics(BaseModel):
    worker_id: str
    name: str
    total_active_time: float
    total_idle_time: float
    total_absent_time: float
    utilization_percentage: float
    total_units_produced: int
    units_per_hour: float


class WorkstationMetrics(BaseModel):
    station_id: str
    name: str
    occupancy_time: float
    utilization_percentage: float
    total_units_produced: int
    throughput_rate: float


class FactoryMetrics(BaseModel):
    total_productive_time: float
    total_production_count: int
    avg_production_rate: float
    avg_utilization: float
