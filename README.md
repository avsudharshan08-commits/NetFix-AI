# NetFix AI – Intelligent Network Hardware Troubleshooter

**FirstCommit '26 – Round 2 Submission**  
**Team:** Druv Kumar (Backend & AI) | Sudarshan (Frontend & Testing Lead)

## Overview
NetFix AI is an intelligent network diagnostic and hardware troubleshooting application designed to move beyond raw command-line outputs. Instead of leaving users to interpret cryptic `ping`, `traceroute`, or `nslookup` logs, NetFix AI ingests live network telemetry or historical log files, detects anomalies using Machine Learning, pinpoints probable hardware or link failures, and provides actionable step-by-step fixes.

## Key Features
- **Dual Diagnostic Modes:** Run real-time network diagnostics against any IP address or domain, or upload `.log`, `.txt`, and `.csv` diagnostic files for offline inspection.
- **Health Scoring & Telemetry Dashboard:** Displays an overall Network Health Score alongside Average Latency, Packet Loss percentage, and DNS Resolution time.
- **Interactive Telemetry Visualization:** Plots latency spikes and packet loss trends over time using Chart.js.
- **ML Anomaly Detection & Root Cause Analysis:** Identifies abnormal jitter, DNS bottlenecks, and hop-level packet drops to distinguish between local hardware/cable faults, router congestion, and upstream ISP issues.
- **Actionable Troubleshooting Engine:** Generates prioritized, plain-English remediation steps tailored to the detected failure mode.

## Tech Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+), Chart.js
- **Backend & AI:** Python, Flask, Flask-CORS, Scikit-Learn / Statistical Anomaly Detection, Subprocess Network Utilities (`ping`, `tracert`, DNS lookup)

## Project Structure
```text
NetFix-AI/
├── frontend/          # Dashboard UI, Chart.js telemetry, and API client
├── backend/           # Flask REST API, network diagnostic runner, and ML engine
├── sample_logs/       # Sample healthy and packet-loss diagnostic logs for testing
└── README.md          # Project documentation