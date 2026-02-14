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
