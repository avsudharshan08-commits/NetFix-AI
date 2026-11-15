@'
# NetFix AI - Intelligent Network Hardware Troubleshooter

**FirstCommit '26 - Round 2 Submission**

**Team:** IOTpro  
**Team Members:** Dhruv Kumar (Team Lead, Backend and AI) | Sudarshan (Frontend and Testing Lead)

---

## 1. Overview

NetFix AI is an intelligent network diagnostic and troubleshooting application that helps users identify network connectivity problems, detect abnormal network behaviour, and understand probable causes of network failures.

Users can run live network diagnostics or upload historical diagnostic log files. The system analyses network metrics, detects anomalies using Machine Learning, identifies probable root causes, and generates actionable troubleshooting recommendations.

## 2. Key Features

### Live Network Diagnostics
- Tests internet connectivity using ping.
- Checks DNS resolution.
- Detects the default network gateway.
- Measures latency and packet loss.
- Performs traceroute to inspect network routes.

### Network Health Dashboard
- Displays an overall network health score.
- Shows average latency, packet loss, and interface errors.
- Displays gateway and DNS status.
- Visualizes network telemetry using Chart.js.

### Diagnostic Log Analysis
- Supports `.log`, `.txt`, and `.csv` uploads.
- Extracts supported network metrics.
- Analyses uploaded data separately from live network measurements.

### Machine Learning Anomaly Detection
- Uses the Isolation Forest algorithm from Scikit-learn.
- Analyses historical network measurements.
- Identifies unusual latency, packet loss, and interface error patterns.
- Distinguishes historical anomalies from current network anomalies.

### Root Cause Analysis
- Uses diagnostic rules to identify probable network problems.
- Detects high latency, packet loss, interface errors, gateway failures, and DNS failures.
- Provides confidence-scored probable causes.

### Troubleshooting Recommendations
- Generates practical recommendations based on detected issues.
- Suggests checks for network cables, adapters, routers, DNS configuration, and network connectivity.

## 3. Technology Stack

| Component | Technologies |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Data Visualization | Chart.js |
| Backend | Python, Flask, Flask-CORS |
| Machine Learning | Scikit-learn, Isolation Forest |
| Numerical Processing | NumPy |
| Network Diagnostics | Ping, Traceroute, Python Socket |
| Version Control | Git and GitHub |

## 4. Project Structure

```text
NetFix-AI/
|
|-- backend/
|   |-- app.py
|   |-- diagnostics.py
|   |-- live_diagnostics.py
|   |-- anomaly_detection.py
|   |-- root_cause.py
|   |-- ai_assistant.py
|   |-- __init__.py
|
|-- frontend/
|   |-- index.html
|   |-- style.css
|   |-- app.js
|
|-- datasets/
|   |-- sample_network_data.csv
|
|-- sample_logs/
|   |-- Healthy and problematic network logs
|
|-- requirements.txt
|-- .gitignore
|-- README.md