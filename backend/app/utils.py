from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Event
import hashlib


def generate_event_hash(event_data: dict) -> str:
    content = f"{event_data['timestamp']}{event_data['worker_id']}{event_data['workstation_id']}{event_data['event_type']}{event_data.get('count', '')}"
    return hashlib.md5(content.encode()).hexdigest()


def is_duplicate(db: Session, event_data: dict) -> bool:
    query = db.query(Event).filter(
        Event.timestamp == event_data["timestamp"],
        Event.worker_id == event_data["worker_id"],
        Event.workstation_id == event_data["workstation_id"],
        Event.event_type == event_data["event_type"],
    )
    if "count" in event_data and event_data["count"] is not None:
        query = query.filter(Event.count == event_data["count"])
    else:
        query = query.filter(Event.count.is_(None))
    return query.first() is not None
