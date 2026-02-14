from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .models import Worker, Workstation, Event, EventType
from .schemas import WorkerMetrics, WorkstationMetrics, FactoryMetrics
from typing import List
import numpy as np

def compute_worker_metrics(db: Session, shift_start: datetime, shift_end: datetime) -> List[WorkerMetrics]:
    workers = db.query(Worker).all()
    metrics = []
    shift_seconds = (shift_end - shift_start).total_seconds()

    for w in workers:
        events = (
            db.query(Event)
            .filter(Event.worker_id == w.worker_id)
            .filter(Event.timestamp >= shift_start)
            .filter(Event.timestamp <= shift_end)
            .order_by(Event.timestamp)
            .all()
        )

        state_events = [e for e in events if e.event_type in (
            EventType.working,
            EventType.idle,
            EventType.absent
        )]

        total_active = total_idle = total_absent = 0.0
        total_units = sum(
            e.count for e in events
            if e.event_type == EventType.product_count and e.count
        )

        current_time = shift_start
        current_state = EventType.absent

        for event in state_events:
            duration = (event.timestamp - current_time).total_seconds()

            if current_state == EventType.working:
                total_active += duration
            elif current_state == EventType.idle:
                total_idle += duration
            else:
                total_absent += duration

            current_state = event.event_type
            current_time = event.timestamp

        # Handle tail
        tail_duration = (shift_end - current_time).total_seconds()
        if current_state == EventType.working:
            total_active += tail_duration
        elif current_state == EventType.idle:
            total_idle += tail_duration
        else:
            total_absent += tail_duration

        utilization = (total_active / shift_seconds * 100) if shift_seconds > 0 else 0
        availability = ((total_active + total_idle) / shift_seconds * 100) if shift_seconds > 0 else 0
        units_per_hour = total_units / (shift_seconds / 3600) if shift_seconds > 0 else 0

        metrics.append(WorkerMetrics(
            worker_id=w.worker_id,
            name=w.name,
            total_active_time=total_active,
            total_idle_time=total_idle,
            total_absent_time=total_absent,
            utilization_percentage=utilization,
            availability_percentage=availability,   # NEW
            effective_working_time=total_active - total_idle,  # NEW
            total_units_produced=total_units,
            units_per_hour=units_per_hour
        ))

    return metrics


def compute_workstation_metrics(db: Session, shift_start: datetime, shift_end: datetime) -> List[WorkstationMetrics]:
    workstations = db.query(Workstation).all()
    metrics = []
    for ws in workstations:
        events = db.query(Event).filter(Event.workstation_id == ws.station_id).order_by(Event.timestamp).all()
        working_events = [e for e in events if e.event_type == EventType.working]
        if not working_events:
            metrics.append(WorkstationMetrics(
                station_id=ws.station_id, name=ws.name,
                occupancy_time=0, utilization_percentage=0,
                total_units_produced=0, throughput_rate=0
            ))
            continue

        times = [e.timestamp for e in working_events] + [shift_end]
        times.sort()
        occupancy = 0.0
        for i, event in enumerate(working_events):
            next_ts = times[i+1] if i+1 < len(times) else shift_end
            occupancy += (next_ts - event.timestamp).total_seconds()

        total_units = sum(e.count for e in events if e.event_type == EventType.product_count and e.count)
        shift_seconds = (shift_end - shift_start).total_seconds()
        util = (occupancy / shift_seconds * 100) if shift_seconds > 0 else 0
        throughput = total_units / (shift_seconds / 3600) if shift_seconds > 0 else 0

        metrics.append(WorkstationMetrics(
            station_id=ws.station_id, name=ws.name,
            occupancy_time=occupancy, utilization_percentage=util,
            total_units_produced=total_units, throughput_rate=throughput
        ))
    return metrics

def compute_factory_metrics(db: Session, shift_start: datetime, shift_end: datetime) -> FactoryMetrics:
    worker_metrics = compute_worker_metrics(db, shift_start, shift_end)
    total_productive_time = sum(w.total_active_time for w in worker_metrics)
    total_production = sum(w.total_units_produced for w in worker_metrics)
    avg_production_rate = np.mean([w.units_per_hour for w in worker_metrics]) if worker_metrics else 0
    avg_utilization = np.mean([w.utilization_percentage for w in worker_metrics]) if worker_metrics else 0
    return FactoryMetrics(
        total_productive_time=total_productive_time,
        total_production_count=total_production,
        avg_production_rate=avg_production_rate,
        avg_utilization=avg_utilization
    )