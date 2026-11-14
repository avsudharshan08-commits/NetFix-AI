import os
import csv

from flask import Flask, request, jsonify
from flask_cors import CORS

from diagnostics import diagnose_network
from anomaly_detection import detect_anomalies
from root_cause import analyze_root_cause
from ai_assistant import generate_recommendations
from live_diagnostics import run_live_diagnostics, run_traceroute

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "datasets",
    "sample_network_data.csv"
)


def load_historical_data():

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError("Historical network dataset not found.")

    network_history = []

    with open(DATASET_PATH, "r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        required_columns = {
            "latency",
            "packet_loss",
            "interface_errors"
        }

        if not required_columns.issubset(set(reader.fieldnames or [])):
            raise ValueError("Historical dataset has invalid columns.")

        for row in reader:

            network_history.append({
                "latency": float(row["latency"]),
                "packet_loss": float(row["packet_loss"]),
                "interface_errors": int(row["interface_errors"])
            })

    return network_history


@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "project": "NetFix AI",
        "message": "Intelligent Network Hardware Troubleshooter",
        "status": "Running",
        "version": "1.0"
    })


@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "Healthy",
        "message": "NetFix AI backend is operational."
    })



@app.route("/api/live-diagnostics", methods=["GET"])
def live_network_diagnostics():

    try:
        report = run_live_diagnostics()

        return jsonify({
            "project": "NetFix AI",
            "success": True,
            "live_diagnostics": report
        }), 200

    except Exception as error:

        app.logger.exception("Live network diagnostics failed")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500



@app.route("/api/traceroute", methods=["GET"])
def traceroute_analysis():

    try:
        destination = request.args.get("host", "8.8.8.8")

        report = run_traceroute(destination)

        return jsonify({
            "project": "NetFix AI",
            "success": True,
            "traceroute": report
        }), 200

    except Exception as error:

        app.logger.exception("Traceroute analysis failed")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

@app.route("/api/analyze", methods=["POST"])
def analyze_network():

    try:

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Please provide valid JSON input."
            }), 400

        required_fields = [
            "latency",
            "packet_loss",
            "interface_errors"
        ]

        for field in required_fields:

            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}"
                }), 400

        metrics = {
            "latency": float(data["latency"]),
            "packet_loss": float(data["packet_loss"]),
            "interface_errors": int(data["interface_errors"]),
            "gateway_reachable": data.get("gateway_reachable", True),
            "dns_working": data.get("dns_working", True)
        }

        if (
            metrics["latency"] < 0
            or metrics["packet_loss"] < 0
            or metrics["packet_loss"] > 100
            or metrics["interface_errors"] < 0
        ):

            return jsonify({
                "error": "Network metrics contain invalid values."
            }), 400

        # Module 1: Network Diagnostics
        diagnostic_report = diagnose_network(metrics)

        # Module 2: Historical Anomaly Detection
        network_history = data.get("network_history")

        if network_history is None:
            network_history = load_historical_data()

        if network_history:

            anomaly_report = detect_anomalies(
                network_history,
                current_metrics=metrics
            )

            anomaly_report["message"] = (
                "Historical and current network anomaly analysis completed successfully."
            )

        else:

            anomaly_report = {
                "message": "At least 5 historical records are required.",
                "total_records": 0,
                "anomalies_detected": 0,
                "normal_records": 0,
                "results": []
            }

        # Module 3: Root Cause Analysis
        root_cause_report = analyze_root_cause(metrics)

        # Module 4: Troubleshooting Recommendations
        recommendation_report = generate_recommendations(
            metrics,
            root_cause_report["probable_causes"]
        )

        return jsonify({
            "project": "NetFix AI",
            "success": True,
            "network_metrics": metrics,
            "diagnostics": diagnostic_report,
            "anomaly_detection": anomaly_report,
            "root_cause_analysis": root_cause_report,
            "troubleshooting_assistant": recommendation_report
        }), 200

    except (ValueError, TypeError, KeyError, FileNotFoundError) as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 400

    except Exception:

        app.logger.exception("Network analysis failed")

        return jsonify({
            "success": False,
            "error": "An internal server error occurred."
        }), 500


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
