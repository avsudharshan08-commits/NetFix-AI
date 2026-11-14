import numpy as np
from sklearn.ensemble import IsolationForest


def detect_anomalies(network_data):
    """
    Detect unusual network behaviour using Isolation Forest.

    Expected input:
    A list of dictionaries containing:
    latency, packet_loss, interface_errors
    """

    if not isinstance(network_data, list) or len(network_data) < 5:
        raise ValueError(
            "At least 5 network records are required for anomaly detection."
        )

    features = []

    for record in network_data:
        try:
            features.append([
                float(record["latency"]),
                float(record["packet_loss"]),
                float(record["interface_errors"])
            ])
        except (KeyError, TypeError, ValueError):
            raise ValueError(
                "Every record must contain valid latency, packet_loss "
                "and interface_errors values."
            )

    data = np.array(features)

    model = IsolationForest(
        contamination=0.2,
        random_state=42
    )

    predictions = model.fit_predict(data)
    anomaly_scores = model.decision_function(data)

    results = []

    for index, prediction in enumerate(predictions):

        is_anomaly = prediction == -1

        results.append({
            "record": index + 1,
            "latency": float(data[index][0]),
            "packet_loss": float(data[index][1]),
            "interface_errors": int(data[index][2]),
            "anomaly": bool(is_anomaly),
            "status": "Anomaly" if is_anomaly else "Normal",
            "anomaly_score": round(float(anomaly_scores[index]), 4)
        })

    total_anomalies = sum(
        1 for result in results if result["anomaly"]
    )

    return {
        "total_records": len(results),
        "anomalies_detected": total_anomalies,
        "normal_records": len(results) - total_anomalies,
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

    report = detect_anomalies(sample_data)

    print("\n========== NETFIX AI ANOMALY REPORT ==========")
    print("Total Records:", report["total_records"])
    print("Anomalies Detected:", report["anomalies_detected"])
    print("Normal Records:", report["normal_records"])

    print("\nDetailed Results:")

    for result in report["results"]:
        print(
            f"Record {result['record']}: "
            f"{result['status']} | "
            f"Latency: {result['latency']} ms | "
            f"Packet Loss: {result['packet_loss']}% | "
            f"Interface Errors: {result['interface_errors']}"
        )

    print("\n==============================================")
