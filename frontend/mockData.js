const MOCK_SCENARIOS = {
  healthy: {
    status: "healthy",
    health_score: 96,
    target: "8.8.8.8",
    metrics: {
      avg_latency_ms: 18.4,
      packet_loss_pct: 0.0,
      jitter_ms: 2.1,
      dns_resolution_ms: 14
    },
    time_series: [
      { timestamp: "10:01", latency: 17, loss: 0 },
      { timestamp: "10:02", latency: 19, loss: 0 },
      { timestamp: "10:03", latency: 18, loss: 0 },
      { timestamp: "10:04", latency: 20, loss: 0 },
      { timestamp: "10:05", latency: 18, loss: 0 }
    ],
    anomaly_detected: false,
    root_cause: "No network anomalies detected. All hops responding within optimal thresholds.",
    recommendations: [
      "Connection is stable; no immediate hardware or DNS changes required.",
      "Continue monitoring if intermittent application-level lag persists."
    ]
  },

  degraded: {
    status: "degraded",
    health_score: 64,
    target: "github.com",
    metrics: {
      avg_latency_ms: 165.2,
      packet_loss_pct: 8.5,
      jitter_ms: 42.0,
      dns_resolution_ms: 230
    },
    time_series: [
      { timestamp: "10:01", latency: 42, loss: 0 },
      { timestamp: "10:02", latency: 190, loss: 10 },
      { timestamp: "10:03", latency: 245, loss: 15 },
      { timestamp: "10:04", latency: 140, loss: 5 },
      { timestamp: "10:05", latency: 209, loss: 12 }
    ],
    anomaly_detected: true,
    root_cause: "High jitter and elevated DNS resolution delay detected on local gateway.",
    recommendations: [
      "Switch primary DNS to Cloudflare (1.1.1.1) or Google (8.8.8.8).",
      "Move closer to the Wi-Fi router or switch from 2.4GHz to 5GHz band.",
      "Close background bandwidth-heavy downloads or cloud syncs."
    ]
  },

  critical: {
    status: "critical",
    health_score: 28,
    target: "Uploaded Log: router_failure.log",
    metrics: {
      avg_latency_ms: 480.0,
      packet_loss_pct: 45.0,
      jitter_ms: 112.5,
      dns_resolution_ms: 890
    },
    time_series: [
      { timestamp: "10:01", latency: 120, loss: 10 },
      { timestamp: "10:02", latency: 540, loss: 50 },
      { timestamp: "10:03", latency: 610, loss: 60 },
      { timestamp: "10:04", latency: 490, loss: 40 },
      { timestamp: "10:05", latency: 640, loss: 65 }
    ],
    anomaly_detected: true,
    root_cause: "Severe packet loss (45%) at Hop 2 indicating failing WAN link or damaged Ethernet cable.",
    recommendations: [
      "Inspect and reseat the RJ45 Ethernet cable between modem and router.",
      "Power-cycle the modem and router for 30 seconds to clear interface errors.",
      "Contact ISP if packet loss persists beyond Hop 2."
    ]
  }
};