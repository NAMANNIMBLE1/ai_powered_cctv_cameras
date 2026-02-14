# AI-Powered Worker Productivity Dashboard

## 📖 Table of Contents

-   Architecture Overview
-   Project Structure
-   Database Schema
-   API Endpoints
-   Sharing the Application with Docker

------------------------------------------------------------------------

# Architecture Overview

The system follows a classic three-tier architecture:

### Edge (AI Cameras)

Computer vision models running on CCTV cameras produce structured
events: - working - idle - absent - product_count

Each event is sent as a JSON payload to the backend API.

### Backend (FastAPI)

-   Ingests events
-   Performs duplicate detection
-   Stores them in SQLite
-   Computes productivity metrics on demand
-   Exposes REST endpoints

### Database (SQLite)

Schema includes: - workers - workstations - events

### Dashboard (React + Vite)

Displays: - Factory-level summary metrics - Worker tables/cards -
Workstation tables/cards - Filtering capabilities


## 📸 Dashboard Screenshots

### Worker Metrics View
![Worker Metrics](assets/Screenshot%202026-02-14%20164203.png)

### Workstation Metrics View
![Workstation Metrics](assets/Screenshot%202026-02-14%20164215.png)

### Factory Overview
![Factory Overview](assets/Screenshot%202026-02-14%20164319.png)


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

------------------------------------------------------------------------

# API Endpoints

  Method   Endpoint                Description
  -------- ----------------------- -----------------------
  POST     /events                 Ingest new event
  POST     /seed                   Regenerate dummy data
  GET      /metrics/workers        Worker metrics
  GET      /metrics/workstations   Workstation metrics
  GET      /metrics/factory        Factory metrics

------------------------------------------------------------------------

# 📤 Sharing the Application with Docker

Once you have built the Docker images, you can easily share the entire
application with others.

## Prerequisites for the Recipient

-   Docker Desktop (or Docker Engine + Docker Compose) installed.
-   Ports 8000 (backend) and 5173 (frontend) free.
-   Ability to create an empty database file.

------------------------------------------------------------------------

## Method 1: Share via Docker Hub (Recommended)

### Step 1: Tag and Push Your Images

``` bash
docker tag worker-monitoring-backend namannimble2627/worker-monitoring-backend:latest
docker tag worker-monitoring-frontend namannimble2627/worker-monitoring-frontend:latest
docker push namannimble2627/worker-monitoring-backend:latest
docker push namannimble2627/worker-monitoring-frontend:latest
```

### Step 2: Prepare docker-compose.yml

``` yaml
services:
  backend:
    image: namannimble2627/worker-monitoring-backend:latest
    ports:
      - "8000:8000"
    volumes:
      - ./backend/production.db:/app/production.db
    environment:
      - DATABASE_URL=sqlite:///./production.db

  frontend:
    image: namannimble2627/worker-monitoring-frontend:latest
    ports:
      - "5173:80"
    depends_on:
      - backend
```

### Step 3: Recipient Setup

Linux/macOS:

``` bash
mkdir -p backend
touch backend/production.db
```

Windows PowerShell:

``` powershell
New-Item -Path .\backend\production.db -ItemType File -Force
```

Run:

``` bash
docker compose up
```

Open: http://localhost:5173

------------------------------------------------------------------------

## Method 2: Share as Tar Files (Offline)

### Export Images

``` bash
docker save -o worker-monitoring-backend.tar worker-monitoring-backend
docker save -o worker-monitoring-frontend.tar worker-monitoring-frontend
```

### Load Images

``` bash
docker load -i worker-monitoring-backend.tar
docker load -i worker-monitoring-frontend.tar
```

### docker-compose.yml (Local Images)

``` yaml
services:
  backend:
    image: worker-monitoring-backend:latest
    ports:
      - "8000:8000"
    volumes:
      - ./backend/production.db:/app/production.db
    environment:
      - DATABASE_URL=sqlite:///./production.db

  frontend:
    image: worker-monitoring-frontend:latest
    ports:
      - "5173:80"
    depends_on:
      - backend
```

Run:

``` bash
docker compose up
```

------------------------------------------------------------------------

## Important Notes

-   The database file must exist before starting containers.
-   CORS is configured for http://localhost:5173.
-   Docker Compose handles networking automatically.
-   Fix permission issues if needed:

``` bash
sudo chown 1000:1000 backend/production.db
```



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
-   Tenant isolation
-   Central analytics via Kafka + ClickHouse

