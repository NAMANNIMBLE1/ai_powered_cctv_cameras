from . import database, metrics, models, schemas, seed
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import utils
from .database import SessionLocal, engine
from typing import List
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Worker Productivity Dashboard")

app = FastAPI(title="Worker Productivity Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    if db.query(models.Worker).count() == 0:
        seed.seed_dummy_data(db)
    db.close()


@app.post("/events", response_model=dict)
def ingest_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    if utils.is_duplicate(db, event.dict()):
        raise HTTPException(status_code=400, detail="Duplicate event")
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return {"status": "ok", "id": db_event.id}


@app.post("/seed")
def regenerate_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(seed.seed_dummy_data, db)
    return {"message": "Seeding started in background"}


@app.get("/metrics/workers", response_model=List[schemas.WorkerMetrics])
def get_worker_metrics(db: Session = Depends(get_db)):
    first = db.query(models.Event).order_by(models.Event.timestamp).first()
    last = db.query(models.Event).order_by(models.Event.timestamp.desc()).first()
    if not first:
        return []
    shift_start = first.timestamp
    shift_end = last.timestamp + timedelta(hours=1)
    return metrics.compute_worker_metrics(db, shift_start, shift_end)


@app.get("/metrics/workstations", response_model=List[schemas.WorkstationMetrics])
def get_workstation_metrics(db: Session = Depends(get_db)):
    first = db.query(models.Event).order_by(models.Event.timestamp).first()
    last = db.query(models.Event).order_by(models.Event.timestamp.desc()).first()
    if not first:
        return []
    shift_start = first.timestamp
    shift_end = last.timestamp + timedelta(hours=1)
    return metrics.compute_workstation_metrics(db, shift_start, shift_end)


@app.get("/metrics/factory", response_model=schemas.FactoryMetrics)
def get_factory_metrics(db: Session = Depends(get_db)):
    first = db.query(models.Event).order_by(models.Event.timestamp).first()
    last = db.query(models.Event).order_by(models.Event.timestamp.desc()).first()
    if not first:
        return schemas.FactoryMetrics(
            total_productive_time=0,
            total_production_count=0,
            avg_production_rate=0,
            avg_utilization=0,
        )
    shift_start = first.timestamp
    shift_end = last.timestamp + timedelta(hours=1)
    return metrics.compute_factory_metrics(db, shift_start, shift_end)
