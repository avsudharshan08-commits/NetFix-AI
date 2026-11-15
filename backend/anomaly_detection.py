import math
import numpy as np
from sklearn.ensemble import IsolationForest


def detect_anomalies(network_data, current_metrics=None):
    """
    Detect anomalies in historical and current network data
    using Isolation Forest.
    """

    if not isinstance(network_data, list) or len(network_data) < 5:
        raise ValueError(
            "At least 5 historical network records are required."
        )

    features = []

    for record in network_data:
        try:
            values = [
                float(record["latency"]),
                float(record["packet_loss"]),
                float(record["interface_errors"])
            ]

            if not all(math.isfinite(value) for value in values):
                raise ValueError

            if any(value < 0 for value in values):
                raise ValueError

            features.append(values)

        except (KeyError, TypeError, ValueError):
            raise ValueError(
                "Every record must contain valid non-negative "
                "latency, packet_loss and interface_errors values."
            )

    historical_count = len(features)

    if current_metrics is not None:
        try:
            current_values = [
                float(current_metrics["latency"]),
                float(current_metrics["packet_loss"]),
                float(current_metrics["interface_errors"])
            ]

            if not all(math.isfinite(value) for value in current_values):
                raise ValueError

            if any(value < 0 for value in current_values):
                raise ValueError

            features.append(current_values)

        except (KeyError, TypeError, ValueError):
            raise ValueError(
                "Current metrics must contain valid non-negative "
                "latency, packet_loss and interface_errors values."
            )

    data = np.array(features, dtype=float)

    model = IsolationForest(
        contamination=0.2,
        random_state=42
    )

    predictions = model.fit_predict(data)
    anomaly_scores = model.decision_function(data)

    results = []

    for index, prediction in enumerate(predictions):

        is_anomaly = prediction == -1
        is_current = index == historical_count and current_metrics is not None

        results.append({
            "record": index + 1,
            "record_type": (
                "Current Network" if is_current else "Historical"
            ),
            "latency": float(data[index][0]),
            "packet_loss": float(data[index][1]),
            "interface_errors": float(data[index][2]),
            "anomaly": bool(is_anomaly),
            "status": "Anomaly" if is_anomaly else "Normal",
            "anomaly_score": round(float(anomaly_scores[index]), 4)
        })

    historical_results = results[:historical_count]

    historical_anomalies = sum(
        1 for result in historical_results if result["anomaly"]
    )

    current_result = (
        results[-1] if current_metrics is not None else None
    )

    total_anomalies = sum(
        1 for result in results if result["anomaly"]
    )

    return {
        "total_records": len(results),
        "historical_records": historical_count,
        "anomalies_detected": total_anomalies,
        "historical_anomalies_detected": historical_anomalies,
        "normal_records": len(results) - total_anomalies,
        "current_network": current_result,
        "results": results
    }


if __name__ == "__main__":

    sample_data = [
        {"latency": 25, "packet_loss": 0, "interface_errors": 0},
        {"latency": 30, "packet_loss": 0, "interface_errors": 1},
        {"latency": 28, "packet_loss": 1, "interface_errors": 0},
        {"latency": 35, "packet_loss": 0, "interface_errors": 2},
        {"latency": 32, "packet_loss": 1, "interface_errors": 1},
        {"latency": 29, "packet_loss": 0, "interface_errors": 0},
        {"latency": 450, "packet_loss": 35, "interface_errors": 150},
        {"latency": 31, "packet_loss": 0, "interface_errors": 1},
        {"latency": 27, "packet_loss": 1, "interface_errors": 0},
        {"latency": 500, "packet_loss": 40, "interface_errors": 200}
    ]

    current_data = {
        "latency": 250,
        "packet_loss": 15,
        "interface_errors": 75
    }

    report = detect_anomalies(sample_data, current_data)

    print("\n========== NETFIX AI ANOMALY REPORT ==========")
    print("Total Records:", report["total_records"])
    print("Historical Anomalies:", report["historical_anomalies_detected"])
    print("Total Anomalies:", report["anomalies_detected"])

    print("\nCurrent Network Analysis:")
    print(report["current_network"])

    print("\nDetailed Results:")

    for result in report["results"]:
        print(
            f"Record {result['record']} "
            f"({result['record_type']}): "
            f"{result['status']} | "
            f"Latency: {result['latency']} ms | "
            f"Packet Loss: {result['packet_loss']}% | "
            f"Interface Errors: {result['interface_errors']}"
        )

    print("\n==============================================")
