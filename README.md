# 🌊 MLStream: Real-Time Distributed MLOps & AI Observability Engine

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![Apache Kafka](https://img.shields.io/badge/Streaming-Apache%20Kafka-black.svg)](https://kafka.apache.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg)](https://nextjs.org/)
[![Prometheus](https://img.shields.io/badge/Telemetry-Prometheus-e6522c.svg)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Dashboards-Grafana-F46800.svg)](https://grafana.com/)
[![Docker](https://img.shields.io/badge/Infrastructure-Docker%20Compose-2496ED.svg)](https://www.docker.com/)

> **Flagship AI Portfolio — Project 7 (Staff MLOps & AI Infrastructure)**  
> An enterprise-grade, fully containerized MLOps observability pipeline. Designed to solve **Silent Model Degradation** by capturing high-throughput live inference traffic, mathematically proving statistical Concept Drift in real-time, and triggering automated healing pipelines.

---

## 🎥 Live System Demo

[![MLStream Live Demo](https://img.youtube.com/vi/Hlua2Sq_o2Q/maxresdefault.jpg)](https://youtu.be/Hlua2Sq_o2Q)

> 🎬 **[Click Here to Watch the 6-Minute Deep Dive Architecture Demo on YouTube](https://youtu.be/Hlua2Sq_o2Q)**  
> *Demonstrating Live Kafka Streaming, Statistical Chaos Injection (Concept Drift), and Automated Model Retraining via Prometheus & Grafana.*

---

## 📌 Executive Summary & Architecture

**MLStream** is built to replicate the exact "Day-2" operations required by Global tech companies. AI models silently fail when real-world data changes (e.g., fraud patterns shift, market volatility). This system prevents financial loss by detecting those shifts mathematically before accuracy drops.

### 🏗️ Enterprise System Architecture
```mermaid
graph TD
    UI["Next.js 14 Dashboard<br>(Control Center & UI)"] <-->|HTTP / REST| API["FastAPI Gateway<br>(Port 8080)"]
    API -->|Inference Logs| K_PROD["Kafka Producer"]
    
    subgraph Event Streaming Broker
    KAFKA["Apache Kafka (Port 9092)"]
    ZOOKEEPER["Zookeeper (Port 2181)"]
    ZOOKEEPER --- KAFKA
    end
    
    K_PROD -->|Publish| KAFKA
    
    subgraph Background Daemon (Async)
    K_CONS["Kafka Consumer Thread"]
    DRIFT["Statistical Drift Engine<br>(KS-Test, Wasserstein)"]
    K_CONS -->|Calculate| DRIFT
    end
    
    KAFKA -->|Consume| K_CONS
    
    DRIFT -->|Update Metrics| PROM_REG["Prometheus Registry"]
    PROM_REG -->|Scrape :9090| PROM["Prometheus TSDB"]
    
    PROM -->|Query| GRAFANA["Grafana MLOps Dashboards<br>(Port 3001)"]
    
    DRIFT -.->|Threshold Breach (p < 0.05)| RETRAIN["Automated Retrain Webhook"]
```

---

## 🎛️ The Command Center: Features & Controls

The system features three integrated observation decks. Here is a breakdown of the interactive UI components:

### 1. Next.js 14 Real-Time Dashboard (`http://localhost:3010`)
* **`[ 🚀 Start Normal Traffic ]`**: Fires up the background simulator. Streams synthetic data matching the original baseline distribution (Mean = 0.0) into the Kafka broker at ~2 req/sec.
* **`[ ⚠️ Inject Concept Drift ]`**: The "Chaos Engineering" button. Instantly shifts the live data distribution mean to `2.5`. This simulates a catastrophic real-world event (e.g., a sudden new financial fraud tactic).
* **`[ 🛑 Stop Stream ]`**: Halts the Kafka traffic simulator.
* **`[ 🔄 Trigger Manual Retrain ]`**: Manually increments the model version (`v1.x.x`) and recalculates the baseline.
* **Feature Statistical Breakdown Table**: Calculates the exact mathematical deviation for all 5 features using a sliding window of the last 50 transactions.
* **Retraining Audit Log**: A chronological ledger showing exactly when the Kafka daemon triggered automated healing due to threshold breaches.

### 2. Grafana MLOps Telemetry (`http://localhost:3001`)
* **Real-Time Drift Score Gauge**: Blends KS-Stat and Earth Mover's Distance into a normalized score out of `1.0`. Turns red when `score > 0.15`.
* **Drift Status Alarm**: Flashes from `STABLE` to `DRIFT DETECTED` the second statistical confidence drops.
* **Inference Throughput (RPS)** & **P95/P99 Latency**: Tracks API health under load.

### 3. FastAPI Gateway (`http://localhost:8080/docs`)
* **`POST /predict`**: Accepts feature vectors, returns prediction UUIDs and class probabilities, and async-publishes to Kafka.
* **`POST /stream/start`**: Asynchronous background task endpoint managing the traffic simulator logic without blocking the main event loop.

---

## 🧮 Mathematical Rigor (Zero Naive Thresholds)

Junior projects detect drift by checking if the "average" changes. **MLStream** utilizes Staff-level mathematical rigor:
1. **Kolmogorov-Smirnov (KS) Test**: Calculates the maximum distance between the live data's Cumulative Distribution Function (CDF) and the baseline CDF. If the **p-value < 0.05**, the system statistically proves the distribution has mutated.
2. **Wasserstein Distance (Earth Mover's Distance)**: Calculates the exact mathematical "cost" to transform the incoming corrupted data distribution back into the baseline shape, providing a severity magnitude for the Grafana gauges.

---

## 🚀 1-Click Reproduction Guide

Run this entire distributed architecture locally in seconds using Docker Compose.

### Prerequisites
* Docker & Docker Desktop installed.
* Ports `3010` (Next.js), `3001` (Grafana), `8080` (FastAPI), `9092` (Kafka), and `9090` (Prometheus) must be free.

### Step-by-Step Execution
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/realtime-mlops-drift-observability.git
   cd realtime-mlops-drift-observability
   ```
2. **Start the Microservices Cluster:**
   ```bash
   docker-compose up -d --build
   ```
3. **Access the Dashboards:**
   * **Next.js UI**: `http://localhost:3010`
   * **Grafana**: `http://localhost:3001` (Prometheus datasource & MLOps dashboards are auto-provisioned).
   * **FastAPI Docs**: `http://localhost:8080/docs`

4. **Shutdown:**
   ```bash
   docker-compose down
   ```

---
*Built as the final capstone for a comprehensive 7-Project Global AI Engineering Portfolio.*
