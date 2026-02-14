# AI-Powered Worker Productivity Dashboard

## 📖 Table of Contents

-   Architecture Overview
-   Project Structure
-   Database Schema
-   Metric Definitions & Assumptions
-   Handling Edge Cases
-   Model Versioning, Drift, and Retraining
-   Scaling Considerations
-   Docker Setup
-   Running the Application
-   API Endpoints

------------------------------------------------------------------------

# Architecture Overview

The system follows a classic three-tier architecture:

### 1️⃣ Edge (AI Cameras)

Computer vision models running on CCTV cameras produce structured
events: - working - idle - absent - product_count

Each event is sent as a JSON payload to the backend API.

### 2️⃣ Backend (FastAPI)

-   Ingests events
-   Performs duplicate detection
-   Stores them in SQLite
-   Computes productivity metrics on demand
-   Exposes REST endpoints

### 3️⃣ Database (SQLite)

Schema includes: - workers - workstations - events

### 4️⃣ Dashboard (React + Vite)

Displays: - Factory-level summary metrics - Worker tables/cards -
Workstation tables/cards - Filtering capabilities

------------------------------------------------------------------------

# Project Structure

    worker_monitoring/
    ├── .gitignore
    ├── docker-compose.yaml
    ├── .env
    ├── production.db
    ├── backend/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── main.py
    │       ├── database.py
    │       ├── models.py
    │       ├── schemas.py
    │       ├── metrics.py
    │       ├── seed.py
    │       └── utils.py
    └── frontend/
        ├── Dockerfile
        └── worker-monitoring/
            ├── package.json
            ├── vite.config.js
            └── src/

------------------------------------------------------------------------

# Database Schema

``` sql
workers:
    id (PK)
    worker_id (unique)
    name

workstations:
    id (PK)
    station_id (unique)
    name

events:
    id (PK)
    timestamp
    worker_id (FK)
    workstation_id (FK)
    event_type ENUM('working','idle','absent','product_count')
    confidence FLOAT NULL
    count INT NULL
```

-   product_count events use the `count` field.
-   Other event types have `count = NULL`.

------------------------------------------------------------------------

# Metric Definitions & Assumptions

## Shift Definition

-   Shift start: first event timestamp
-   Shift end: last event timestamp + 1 hour
-   If no events → metrics return zero

## State Durations

Duration = time until next event for same worker. If no next event →
lasts until shift end.

## Worker-Level Metrics

  Metric                 Formula
  ---------------------- ---------------------------
  Total active time      Sum of working durations
  Total idle time        Sum of idle durations
  Total absent time      Sum of absent durations
  Utilization %          (active / total) \* 100
  Total units produced   Sum(product_count.count)
  Units per hour         total_units / shift_hours

## Workstation-Level Metrics

  Metric            Formula
  ----------------- ------------------------------------
  Occupancy time    Sum of working durations
  Utilization %     (occupancy / shift_seconds) \* 100
  Total units       Sum(product_count.count)
  Throughput rate   total_units / shift_hours

## Factory-Level Metrics

  Metric                    Formula
  ------------------------- ---------------------------------
  Total productive time     Sum of all workers' active time
  Total production count    Sum of all workers' units
  Average production rate   Mean(units per hour)
  Average utilization       Mean(worker utilization %)

------------------------------------------------------------------------

# Handling Edge Cases

## Intermittent Connectivity

-   Cameras buffer events locally
-   Retry with exponential backoff
-   Store-and-forward recommended

## Duplicate Events

Duplicate detection based on: (timestamp, worker_id, workstation_id,
event_type, count)

## Out-of-Order Timestamps

Events are sorted during metric computation.

------------------------------------------------------------------------

# Model Versioning, Drift & Retraining

## Model Versioning

Add `model_version` column in events table. Create `model_deployments`
table.

## Detecting Drift

Monitor: - Confidence score distribution - Event type ratios -
Statistical tests (KS test)

## Retraining Strategy

-   Alert on drift
-   Trigger retraining
-   Shadow deploy
-   A/B test before rollout

------------------------------------------------------------------------

# Scaling Considerations

## From 5 → 100+ Cameras

  Layer       Recommendation
  ----------- -------------------------------
  Database    PostgreSQL / TimescaleDB
  API         Load balancer (Nginx)
  Ingestion   Kafka / RabbitMQ
  Metrics     Background jobs + Redis cache

## Multi-Site

-   Regional backend per site
-   Central aggregator
-   Central analytics via Kafka + ClickHouse

------------------------------------------------------------------------

# Docker Setup

## Using Docker Compose

    docker compose up --build

Ports: - Backend: http://localhost:8000 - Swagger:
http://localhost:8000/docs - Frontend: http://localhost:5173

Stop containers:

    docker compose down

Reset DB:

    docker compose down -v

------------------------------------------------------------------------

# Running Without Docker

## Backend

    cd backend
    python -m venv venv or uv venv venv  
    source venv/Scripts/activate in linux use bin instead of Scripts  
    uv pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000

## Frontend

    cd frontend/worker-monitoring
    npm install
    npm run dev

------------------------------------------------------------------------

# API Endpoints

  Method   Endpoint                Description
  -------- ----------------------- -----------------------
  POST     /events                 Ingest new event
  POST     /seed                   Regenerate dummy data
  GET      /metrics/workers        Worker metrics
  GET      /metrics/workstations   Workstation metrics
  GET      /metrics/factory        Factory metrics

All endpoints return JSON. Swagger documentation available at:
http://localhost:8000/docs
