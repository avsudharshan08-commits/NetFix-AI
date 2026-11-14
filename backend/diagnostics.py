def diagnose_network(metrics):
    """
    Analyse network metrics and identify potential network problems.
    """

    issues = []
    recommendations = []

    latency = metrics.get("latency", 0)
    packet_loss = metrics.get("packet_loss", 0)
    interface_errors = metrics.get("interface_errors", 0)
    gateway_reachable = metrics.get("gateway_reachable", True)
    dns_working = metrics.get("dns_working", True)

    # Latency analysis
    if latency > 200:
        issues.append("Critical network latency detected.")
        recommendations.append(
            "Inspect network congestion, routing and device performance."
        )
    elif latency > 100:
        issues.append("High network latency detected.")
        recommendations.append(
            "Check network traffic and routing performance."
        )

    # Packet loss analysis
    if packet_loss > 10:
        issues.append("Critical packet loss detected.")
        recommendations.append(
            "Inspect network cables, wireless signal and network links."
        )
    elif packet_loss > 2:
        issues.append("Moderate packet loss detected.")
        recommendations.append(
            "Check network stability and possible congestion."
        )

    # Network interface analysis
    if interface_errors > 50:
        issues.append("High network interface errors detected.")
        recommendations.append(
            "Inspect network interface statistics and physical connections."
        )
    elif interface_errors > 0:
        issues.append("Network interface errors detected.")
        recommendations.append(
            "Check network adapter drivers and interface configuration."
        )

    # Gateway analysis
    if not gateway_reachable:
        issues.append("Default gateway is unreachable.")
        recommendations.append(
            "Check router connectivity, gateway configuration and cables."
        )

    # DNS analysis
    if not dns_working:
        issues.append("DNS resolution failure detected.")
        recommendations.append(
            "Check DNS server settings and test an alternative DNS server."
        )

    # Overall network status
    if any("Critical" in issue for issue in issues):
        status = "Critical"
    elif issues:
        status = "Warning"
    else:
        status = "Healthy"

    if not issues:
        issues.append("No significant network problems detected.")
        recommendations.append(
            "Continue monitoring network performance."
        )

    return {
        "status": status,
        "issues": issues,
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

    report = diagnose_network(sample_metrics)

    print("\n========== NETFIX AI DIAGNOSTIC REPORT ==========")
    print("\nNetwork Status:", report["status"])

    print("\nDetected Issues:")
    for issue in report["issues"]:
        print("-", issue)

    print("\nRecommendations:")
    for recommendation in report["recommendations"]:
        print("-", recommendation)

    print("\n=================================================")
