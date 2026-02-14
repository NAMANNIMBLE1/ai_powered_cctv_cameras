from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum


class EventType(str, enum.Enum):
    working = "working"
    idle = "idle"
    absent = "absent"
    product_count = "product_count"


class Worker(Base):
    __tablename__ = "workers"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String, unique=True, index=True)
    name = Column(String)


class Workstation(Base):
    __tablename__ = "workstations"
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String, unique=True, index=True)
    name = Column(String)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    worker_id = Column(String, ForeignKey("workers.worker_id"))
    workstation_id = Column(String, ForeignKey("workstations.station_id"))
    event_type = Column(Enum(EventType))
    confidence = Column(Float, nullable=True)
    count = Column(Integer, nullable=True)

    worker = relationship("Worker")
    workstation = relationship("Workstation")
