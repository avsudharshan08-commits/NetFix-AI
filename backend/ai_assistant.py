def generate_recommendations(metrics, probable_causes):
    """
    Generate troubleshooting recommendations
    based on network metrics and probable causes.
    """

    recommendations = []

    latency = float(metrics.get("latency", 0))
    packet_loss = float(metrics.get("packet_loss", 0))
    interface_errors = int(metrics.get("interface_errors", 0))

    gateway_reachable = metrics.get("gateway_reachable", True)
    dns_working = metrics.get("dns_working", True)

    if latency > 200:
        recommendations.extend([
            "Check network bandwidth utilization.",
            "Identify devices consuming excessive bandwidth.",
            "Inspect router and switch performance."
        ])

    if packet_loss > 10:
        recommendations.extend([
            "Inspect Ethernet cables and network connections.",
            "Check Wi-Fi signal strength and interference.",
            "Test the connection using another network cable."
        ])

    if interface_errors > 50:
        recommendations.extend([
            "Check network adapter statistics.",
            "Inspect physical network ports and connections.",
            "Update or reinstall network adapter drivers if necessary."
        ])

    if not gateway_reachable:
        recommendations.extend([
            "Check whether the router is powered on.",
            "Verify the default gateway IP configuration.",
            "Test connectivity between the computer and router."
        ])

    if not dns_working:
        recommendations.extend([
            "Check DNS server availability.",
            "Verify DNS configuration.",
            "Try resolving the domain using another DNS server."
        ])

    if not recommendations:
        recommendations.append(
            "Network appears healthy. Continue monitoring latency and packet loss."
        )

    recommendations = list(dict.fromkeys(recommendations))

    return {
        "total_recommendations": len(recommendations),
        "recommendations": recommendations
    }


if __name__ == "__main__":

    sample_metrics = {
        "latency": 250,
        "packet_loss": 15,
        "interface_errors": 75,
        "gateway_reachable": True,
        "dns_working": True
    }

    sample_causes = [
        "Network Congestion",
        "Unstable Network Connection",
        "Network Interface Errors"
    ]

    report = generate_recommendations(
        sample_metrics,
        sample_causes
    )

    print("\n========== NETFIX AI TROUBLESHOOTING ASSISTANT ==========")

    print("Total Recommendations:", report["total_recommendations"])

    for index, recommendation in enumerate(
        report["recommendations"], start=1
    ):
        print(f"{index}. {recommendation}")

    print("\n=========================================================")
