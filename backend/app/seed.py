from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from .models import Worker, Workstation, Event, EventType


def seed_dummy_data(db: Session):
    db.query(Event).delete()
    db.query(Worker).delete()
    db.query(Workstation).delete()

    workers = [
        Worker(worker_id="W1", name="Alice"),
        Worker(worker_id="W2", name="Bob"),
        Worker(worker_id="W3", name="Charlie"),
        Worker(worker_id="W4", name="Diana"),
        Worker(worker_id="W5", name="Eve"),
        Worker(worker_id="W6", name="Frank"),
    ]
    db.add_all(workers)

    workstations = [
        Workstation(station_id="S1", name="Assembly"),
        Workstation(station_id="S2", name="Packaging"),
        Workstation(station_id="S3", name="Quality Check"),
        Workstation(station_id="S4", name="Welding"),
        Workstation(station_id="S5", name="Painting"),
        Workstation(station_id="S6", name="Shipping"),
    ]
    db.add_all(workstations)
    db.commit()

    shift_start = datetime(2026, 1, 15, 9, 0, 0)
    shift_end = datetime(2026, 1, 15, 17, 0, 0)

    for worker in workers:
        current_time = shift_start
        state = EventType.working
        while current_time < shift_end:
            duration = random.randint(5, 60)
            next_time = current_time + timedelta(minutes=duration)
            if next_time > shift_end:
                next_time = shift_end

            event = Event(
                timestamp=current_time,
                worker_id=worker.worker_id,
                workstation_id=random.choice(workstations).station_id,
                event_type=state,
                confidence=random.uniform(0.8, 1.0),
                count=None,
            )
            db.add(event)

            if state == EventType.working and random.random() > 0.7:
                prod_time = current_time + timedelta(
                    minutes=random.randint(1, max(1, duration - 1))
                )
                prod_event = Event(
                    timestamp=prod_time,
                    worker_id=worker.worker_id,
                    workstation_id=event.workstation_id,
                    event_type=EventType.product_count,
                    confidence=random.uniform(0.9, 1.0),
                    count=random.randint(1, 10),
                )
                db.add(prod_event)

            state = random.choice([EventType.working, EventType.idle, EventType.absent])
            current_time = next_time

    db.commit()
