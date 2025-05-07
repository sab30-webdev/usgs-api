# USGS Earthquake API Service

A scalable, containerized FastAPI microservice that provides real-time earthquake extending the [USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/). Includes Redis-based caching and Docker Swarm support for replication and high availability.

---

## 🚀 Features

- FastAPI-powered RESTful API
- Real-time earthquake data from USGS
- Caching using Redis to reduce API latency and rate limits
- Scalable with Docker Swarm
- Basic structured logging
- Modular code structure

---

## 🧰 Prerequisites

- [Docker](https://www.docker.com/) must be installed and running on your system.

---

## 🧱 Tech Stack and Image

- **FastAPI**
- **Uvicorn** (ASGI server)
- **HTTPX** (async HTTP client)
- **Docker & Docker Swarm**
- **python:3.12.10-slim** (Application base image)
- **redis:7** (caching image: In-memory data store used as a caching layer)

---

## 📌 Assumptions

We assume that the San Francisco Bay Area is approximated by latitude(37.7749)/longitude(-122.4194) around with a radius of 100km.

Cache expiry is set to 30 seconds to align with API throttling requirement.

/earthquakes/tsunami-alerts responses are sparse; response may often be empty.

---

## 📁 Project Structure

```
project-root/
├── app/                        # Application source code
│   ├── config.py               # Environment config
│   ├── logging_config.py       # Logging setup
│   ├── main.py                 # FastAPI entrypoint
│   ├── api/endpoints.py        # API routes
│   ├── services/
│   │   ├── cache.py            # Redis caching logic
│   │   └── usgs.py             # USGS API interaction
│   └── utils/state_coordinates.py # State/region utilities
├── Dockerfile                 # Docker build
├── requirements.txt           # Python dependencies
├── stack.yml                  # Docker Swarm deployment
└── .gitignore
```

---

## 📦 System Architecture

```
           ┌──────────────┐       ┌─────────────┐
Client --> │  API Replica │ <---> │             │
           └──────────────┘       │             │
           ┌──────────────┐       │             │
Client --> │  API Replica │ <---> │   Redis     │
           └──────────────┘       │  (Shared)   │
           ┌──────────────┐       │             │
Client --> │  API Replica │ <---> │             │
           └──────────────┘       └─────────────┘
```

---

## 🐳 How to Run the Application

### 1. Build the Docker Image

Build the Docker image and tag it as `usgs-api`:

```bash
docker build -t usgs-api .
```

### 2. Initialize Docker Swarm and Deploy the Stack

Initialize Docker Swarm (if not already initialized) and deploy the application using the provided `stack.yml` file. This deploys the stack with the service name `usgs-stack`:

```bash
docker swarm init
docker stack deploy -c stack.yml usgs-stack
```

### 3. Check Running Services and Replicas

Use this command to view the services running in the stack along with their replica counts. You should see **3 replicas of the API service** and **1 Redis container** running:

```bash
docker service ls
```

### 4. Scale the API Service

To scale the API service from 3 to 6 replicas:

```bash
docker service scale usgs-stack_api=6
```

### 5. View Live Logs

To stream logs from the API service in real-time (e.g., when accessed via browser or `curl`):

```bash
docker service logs -f usgs-stack_api
```

---

## API Usage

Example requests

### 1. Health Check

Endpoint: /

```bash
curl http://localhost:8000
```

Response:

```bash
"Welcome to USGS"
```

### 2. Retrieve all earthquakes M2.0+ for the San Francisco Bay Area during a specific time range

Endpoint: /v1/earthquakes/sf-bay-area

```bash
curl http://localhost:8000/v1/earthquakes/sf-bay-area?start_time=2025-01-10&end_time=2025-04-22
```

Response:

```bash
{
  "type": "FeatureCollection",
  "metadata": {
    "generated": 1746507320000,
    "url": "https://earthquake.usgs.gov/fdsnws/event/1/query?starttime=2025-01-10&endtime=2025-04-22&format=geojson&minmagnitude=2.0&latitude=37.7749&longitude=-122.4194&maxradiuskm=100",
    "title": "USGS Earthquakes",
    "status": 200,
    "api": "1.14.1",
    "count": 56
  },
  "features": [
    {
      "type": "Feature",
      "properties": {
        "mag": 2.92,
        "place": "13 km NNE of Pittsburg, CA",
        "time": 1743781060370,
        "updated": 1745516633040,
        "tz": null,
        "url": "https://earthquake.usgs.gov/earthquakes/eventpage/nc75160067",
        "detail": "https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=nc75160067&format=geojson",
        "felt": 33,
        "cdi": 3.1,
        "mmi": null,
        "alert": null,
        "status": "reviewed",
        "tsunami": 0,
        "sig": 141,
        "net": "nc",
        "code": "75160067",
        "ids": ",nc75160067,us6000q3yf,",
        "sources": ",nc,us,",
        "types": ",dyfi,focal-mechanism,nearby-cities,origin,phase-data,scitech-link,",
        "nst": 150,
        "dmin": 0.03748,
        "rms": 0.26,
        "gap": 46,
        "magType": "ml",
        "type": "earthquake",
        "title": "M 2.9 - 13 km NNE of Pittsburg, CA"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-121.847166666667, 38.1385, 27.16]
      },
      "id": "nc75160067"
    },
    .
    .
    .
```

### 3. Retrieve all earthquakes M2.0+ that have 10+ felt reports for the San Francisco Bay Area during a specific time range

Endpoint: /v1/earthquakes/sf-bay-area/felt-reports

```bash
curl http://localhost:8000/v1/earthquakes/sf-bay-area/felt-reports?start_time=2024-12-10&end_time=2025-02-20
```

Response:

```bash
{
  "type": "FeatureCollection",
  "metadata": {
    "generated": 1746507630000,
    "url": "https://earthquake.usgs.gov/fdsnws/event/1/query?starttime=2024-12-10&endtime=2025-02-20&format=geojson&minmagnitude=2.0&latitude=37.7749&longitude=-122.4194&maxradiuskm=100&minfelt=10",
    "title": "USGS Earthquakes",
    "status": 200,
    "api": "1.14.1",
    "count": 20
  },
  "features": [
    {
      "type": "Feature",
      "properties": {
        "mag": 2.68,
        "place": "7 km W of Kenwood, CA",
        "time": 1739929545940,
        "updated": 1742350773040,
        "tz": null,
        "url": "https://earthquake.usgs.gov/earthquakes/eventpage/nc75135942",
        "detail": "https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=nc75135942&format=geojson",
        "felt": 90,
        "cdi": 3.8,
        "mmi": null,
        "alert": null,
        "status": "reviewed",
        "tsunami": 0,
        "sig": 145,
        "net": "nc",
        "code": "75135942",
        "ids": ",nc75135942,us7000pen6,",
        "sources": ",nc,us,",
        "types": ",dyfi,focal-mechanism,nearby-cities,origin,phase-data,scitech-link,",
        "nst": 130,
        "dmin": 0.03246,
        "rms": 0.12,
        "gap": 29,
        "magType": "md",
        "type": "earthquake",
        "title": "M 2.7 - 7 km W of Kenwood, CA"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-122.622666666667, 38.3963333333333, 9.52]
      },
      "id": "nc75135942"
    },
    .
    .
    .
```

### 4. Retrieve all earthquakes M2.0+ for the past day that had tsunami alerts for any given US state.

Endpoint: /v1/earthquakes/tsunami-alerts

NOTE: Code logic has been modified to filter earthquake data that did not trigger tsunami alerts since there are very few instances that match the scenario , the API will most likey return empty json

```bash
curl http://localhost:8000/v1/earthquakes/tsunami-alerts?state=Washington
```

Response:

```bash
{
  "count": 1,
  "earthquakes": [
    {
      "type": "Feature",
      "properties": {
        "mag": 2.06,
        "place": "8 km ESE of Loomis, Washington",
        "time": 1746488767550,
        "updated": 1746506252050,
        "tz": null,
        "url": "https://earthquake.usgs.gov/earthquakes/eventpage/uw62094437",
        "detail": "https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=uw62094437&format=geojson",
        "felt": null,
        "cdi": null,
        "mmi": null,
        "alert": null,
        "status": "reviewed",
        "tsunami": 0,
        "sig": 65,
        "net": "uw",
        "code": "62094437",
        "ids": ",uw62094437,",
        "sources": ",uw,",
        "types": ",origin,phase-data,",
        "nst": 11,
        "dmin": 0.0986,
        "rms": 0.35,
        "gap": 123,
        "magType": "ml",
        "type": "earthquake",
        "title": "M 2.1 - 8 km ESE of Loomis, Washington"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-119.527666666667, 48.803, 16.5]
      },
      "id": "uw62094437"
    }
  ]
}
.
.
.
```

---

## ⛔ Request Deduplication with Redis Cache

To ensure we **do not overload the USGS service**, our application implements a **caching layer using Redis**. This prevents the same request from being made more than once within a **30-second window**.

### ✅ How It Works

- Each unique API request (based on query parameters like latitude, longitude, magnitude, etc.) is assigned a **cache key**.
- When a request is received:
  1. The app checks Redis to see if a cached response exists for the given key.
  2. If found, it serves the cached response immediately.
  3. If not found, it makes a **single request to the USGS API**, stores the response in Redis with a **TTL of 30 seconds**, and returns it to the user.
- This approach reduces redundant external calls, **enhances performance**, and **protects the USGS API from abuse**.

---

## 🐳 Docker Swarm Cluster Setup (Scalability Experiment)

To validate the service's scalability in a container orchestration environment, a Docker Swarm cluster was set up using two EC2 instances:

- **1 Manager Node**
- **1 Worker Node**

### 🛠️ Cluster Initialization

The Swarm cluster was initialized on the manager node. A join token was generated and used on the worker node to securely join the cluster:

```bash
docker swarm join --token <worker-token> <manager-ip>:2377
```

Once the worker successfully joined, the cluster nodes were verified:

```bash
docker node ls

ID                            HOSTNAME                                      STATUS    AVAILABILITY   MANAGER STATUS   ENGINE VERSION
n8mfdqyydmhwpru7seh3wlhnz *   ip-172-31-1-195.eu-north-1.compute.internal   Ready     Active         Leader           25.0.8
vhm8u6ybwhxwv0egl86f0blqh     ip-172-31-11-97.eu-north-1.compute.internal   Ready     Active                          25.0.8
```

### 📦 Service Deployment and Scaling

The image was deployed to docker public registry and updated the `stack.yml` with the corresponding public image

The docker `stack.yml` file was deployed to the Swarm manager, which automatically scheduled services across both nodes. The `usgs-stack_api` service was then scaled to **10 replicas** to simulate high-load scenarios and test horizontal scaling:

```bash
docker service scale usgs-stack_api=10
```

Service status after scaling:

```bash
docker service ls

NAME               MODE         REPLICAS   IMAGE
usgs-stack_api     replicated   10/10      usgs-api
usgs-stack_redis   replicated   1/1        redis:7
```

### 🧭 Container Distribution

The Docker Swarm scheduler intelligently distributed containers across the manager and worker nodes.

#### ✅ Manager Node Containers

```bash
docker ps

usgs-stack_api.5
usgs-stack_api.6
usgs-stack_api.7
usgs-stack_api.9
usgs-stack_api.2
usgs-stack_redis.1
```

#### ✅ Worker Node Containers

```bash
docker ps

usgs-stack_api.1
usgs-stack_api.3
usgs-stack_api.4
usgs-stack_api.8
usgs-stack_api.10
```

### 🌐 API Access

The deployed API is accessible via the node's public IP and ready to serve API requests

**http://16.16.159.146:8000**

---

## Whats Next?

### Autoscaling Strategy

To ensure the service remains responsive under varying loads, autoscaling can be implemented using industry-standard platforms and observability tools. Here's how autoscaling would be approached in different environments:

🚀 Kubernetes (K8s)
In a Kubernetes deployment, Horizontal Pod Autoscaler (HPA) can be used to automatically scale the number of pods based on resource usage metrics like CPU or memory. For more advanced use cases, HPA can also scale based on custom metrics (e.g., request rate or response latency) when integrated with Prometheus and the Kubernetes Metrics Adapter.

☁️ AWS ECS
In AWS ECS (Elastic Container Service), Service Auto Scaling can be configured to automatically adjust the number of running task instances based on CloudWatch metrics such as average CPU or memory usage.

📈 Prometheus for Observability and Custom Metrics
Prometheus plays a central role in enabling observability and autoscaling by collecting real-time metrics from the application. These metrics provide valuable insights into the system’s behavior and performance, and can be used to make informed scaling decisions.

Key metrics monitored include:

Request Rate: Number of incoming API requests per second

Cache Efficiency: Ratio of cache hits to total requests, helping optimize Redis usage

Response Time: Latency of API responses, useful for detecting performance bottlenecks

Error Rate: Frequency of 4xx and 5xx responses, indicating potential reliability issues

These metrics are exposed via a /metrics endpoint and scraped by Prometheus at regular intervals. When integrated with Kubernetes HPA or AWS CloudWatch (via exporters), they enable custom, metric-based autoscaling to maintain optimal performance under varying workloads.
