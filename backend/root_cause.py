def analyze_root_cause(metrics):
    latency = float(metrics.get("latency", 0))
    packet_loss = float(metrics.get("packet_loss", 0))
    interface_errors = int(metrics.get("interface_errors", 0))

    gateway_reachable = metrics.get("gateway_reachable", True)
    dns_working = metrics.get("dns_working", True)

    causes = []

    if latency > 200:
        causes.append({
            "cause": "Network Congestion",
            "confidence": "High",
            "explanation": "High latency indicates possible network congestion or overloaded network equipment."
        })

    if packet_loss > 10:
        causes.append({
            "cause": "Unstable Network Connection",
            "confidence": "High",
            "explanation": "Packet loss may indicate damaged cables, weak wireless signals or unstable network links."
        })

    if interface_errors > 50:
        causes.append({
            "cause": "Network Interface Errors",
            "confidence": "High",
            "explanation": "High interface errors may indicate connection problems or network adapter issues."
        })

    if not gateway_reachable:
        causes.append({
            "cause": "Gateway Connectivity Failure",
            "confidence": "High",
            "explanation": "The default gateway is unreachable. Check router connectivity and network configuration."
        })

    if not dns_working:
        causes.append({
            "cause": "DNS Resolution Failure",
            "confidence": "High",
            "explanation": "DNS resolution is failing. Check DNS server availability and configuration."
        })

    if not causes:
        causes.append({
            "cause": "No Major Network Issue Detected",
            "confidence": "High",
            "explanation": "The supplied metrics do not indicate any major known network problem."
        })

    return {
        "total_causes": len(causes),
        "probable_causes": causes
    }


if __name__ == "__main__":

    sample_metrics = {
        "latency": 250,
        "packet_loss": 15,
        "interface_errors": 75,
        "gateway_reachable": True,
        "dns_working": True
    }

    report = analyze_root_cause(sample_metrics)

    print("\n========== NETFIX AI ROOT CAUSE REPORT ==========")
    print("Total Probable Causes:", report["total_causes"])

    for index, cause in enumerate(report["probable_causes"], start=1):
        print(f"\nCause {index}: {cause['cause']}")
        print("Confidence:", cause["confidence"])
        print("Explanation:", cause["explanation"])

    print("\n=================================================")
