const API_BASE = "http://127.0.0.1:5000";
let telemetryChart = null;

document.addEventListener("DOMContentLoaded", async () => {
  document.getElementById("runDiagBtn").addEventListener("click", runFullLivePipeline);
  document.getElementById("uploadLogBtn").addEventListener("click", handleLogOrCsvUpload);
  document.getElementById("dataMode").addEventListener("change", (e) => {
    if (e.target.value === "mock") loadMockFallback();
    else runFullLivePipeline();
  });

  const healthy = await checkBackendHealth();
  if (healthy) {
    runFullLivePipeline();
  } else {
    document.getElementById("dataMode").value = "mock";
    loadMockFallback();
  }
});

async function checkBackendHealth() {
  const pill = document.getElementById("apiStatus");
  const text = document.getElementById("apiStatusText");
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    const data = await res.json();
    if (res.ok && data.status) {
      pill.className = "api-status online";
      text.textContent = `Flask API: ${data.status}`;
      return true;
    }
  } catch (_) {}
  pill.className = "api-status offline";
  text.textContent = "Flask API Offline (Demo Mode)";
  return false;
}

async function runFullLivePipeline() {
  if (document.getElementById("dataMode").value === "mock") {
    loadMockFallback();
    return;
  }

  const host = document.getElementById("targetHost").value.trim() || "8.8.8.8";
  clearError();
  setLoading(true);

  try {
    // 1. Fetch Live Diagnostics & Traceroute in parallel
    const [diagRes, traceRes] = await Promise.all([
      fetch(`${API_BASE}/api/live-diagnostics`),
      fetch(`${API_BASE}/api/traceroute?host=${encodeURIComponent(host)}`)
    ]);

    const diagJson = await diagRes.json();
    const traceJson = await traceRes.json();

    if (!diagRes.ok || !diagJson.success) {
      throw new Error(diagJson.error || "Live diagnostics endpoint failed.");
    }

    const live = diagJson.live_diagnostics || {};
    const hops = extractTracerouteHops(traceJson.traceroute);
    renderRouteMap(hops, host);

    // 2. Map live metrics into POST /api/analyze for Isolation Forest + Root Cause + AI Fixes
    const latency = Number(live.avg_latency_ms ?? live.latency_ms ?? live.latency ?? 25);
    const packetLoss = Number(live.packet_loss_pct ?? live.packet_loss ?? 0);
    const interfaceErrors = Number(live.interface_errors ?? 0);
    const gatewayOk = Boolean(live.gateway_reachable ?? live.gateway_ok ?? true);
    const dnsOk = Boolean(live.dns_working ?? live.dns_ok ?? true);

    const analyzeRes = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        latency,
        packet_loss: packetLoss,
        interface_errors: interfaceErrors,
        gateway_reachable: gatewayOk,
        dns_working: dnsOk
      })
    });

    const analyzeJson = await analyzeRes.json();
    if (!analyzeRes.ok || !analyzeJson.success) {
      throw new Error(analyzeJson.error || "ML & Root Cause analysis failed.");
    }

    const series = hops.length
      ? hops.map((h) => ({ label: `Hop ${h.hop}`, latency: h.rtt, loss: h.loss }))
      : [
          { label: "Gateway", latency: Math.max(2, +(latency * 0.2).toFixed(1)), loss: 0 },
          { label: "ISP Edge", latency: Math.max(5, +(latency * 0.6).toFixed(1)), loss: packetLoss / 2 },
          { label: host, latency, loss: packetLoss }
        ];

    updateDashboardUI({
      latency,
      packetLoss,
      interfaceErrors,
      gatewayOk,
      dnsOk,
      analyze: analyzeJson,
      series
    });
  } catch (err) {
    showError(`${err.message} (Ensure 'python backend/app.py' is running on port 5000)`);
  } finally {
    setLoading(false);
  }
}

async function handleLogOrCsvUpload() {
  const file = document.getElementById("logFileInput").files[0];
  if (!file) {
    showError("Please select a .log, .txt, or .csv network diagnostic file first.");
    return;
  }

  clearError();
  setLoading(true);

  try {
    const rawText = await file.text();
    const parsed = parseDiagnosticFile(rawText, file.name);

    if (document.getElementById("dataMode").value === "mock") {
      loadMockFallback("critical");
      setLoading(false);
      return;
    }

    const analyzeRes = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        latency: parsed.avgLatency,
        packet_loss: parsed.packetLoss,
        interface_errors: parsed.interfaceErrors,
        gateway_reachable: parsed.packetLoss < 80,
        dns_working: parsed.packetLoss < 50,
        ...(parsed.history.length >= 5 ? { network_history: parsed.history } : {})
      })
    });

    const analyzeJson = await analyzeRes.json();
    if (!analyzeRes.ok || !analyzeJson.success) {
      throw new Error(analyzeJson.error || "Backend failed to analyze uploaded log.");
    }

    renderRouteMap(
      [
        { hop: 1, ip: "Local Gateway (192.168.1.1)", rtt: 4, loss: 0 },
        { hop: 2, ip: `Log Source: ${file.name}`, rtt: parsed.avgLatency, loss: parsed.packetLoss }
      ],
      file.name
    );

    updateDashboardUI({
      latency: parsed.avgLatency,
      packetLoss: parsed.packetLoss,
      interfaceErrors: parsed.interfaceErrors,
      gatewayOk: parsed.packetLoss < 80,
      dnsOk: parsed.packetLoss < 50,
      analyze: analyzeJson,
      series: parsed.series
    });
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
}

function parseDiagnosticFile(text, fileName) {
  const lines = text.split(/\r?\n/).filter((l) => l.trim());
  const series = [];
  const history = [];
  let totalPackets = 0;
  let lostPackets = 0;
  let interfaceErrors = 0;

  if (fileName.toLowerCase().endsWith(".csv")) {
    lines.slice(1).forEach((line, idx) => {
      const cols = line.split(",").map((c) => c.trim());
      const lat = parseFloat(cols[0]) || 0;
      const loss = parseFloat(cols[1]) || 0;
      const errs = parseInt(cols[2], 10) || 0;
      interfaceErrors = Math.max(interfaceErrors, errs);
      series.push({ label: `Rec ${idx + 1}`, latency: lat, loss });
      history.push({ latency: lat, packet_loss: loss, interface_errors: errs });
    });
  } else {
    lines.forEach((line) => {
      const replyMatch = line.match(/time[=<]\s*([\d.]+)\s*ms/i);
      if (replyMatch) {
        totalPackets++;
        const lat = parseFloat(replyMatch[1]);
        series.push({ label: `Pkt ${totalPackets}`, latency: lat, loss: 0 });
        history.push({ latency: lat, packet_loss: 0, interface_errors: 0 });
      } else if (/timed out|unreachable|failure/i.test(line)) {
        totalPackets++;
        lostPackets++;
        series.push({ label: `Pkt ${totalPackets}`, latency: 0, loss: 100 });
        history.push({ latency: 500, packet_loss: 100, interface_errors: 2 });
      }
      const errMatch = line.match(/errors?[:=\s]+(\d+)/i);
      if (errMatch) interfaceErrors += parseInt(errMatch[1], 10);
    });
  }

  const validLatencies = series.filter((s) => s.latency > 0).map((s) => s.latency);
  const avgLatency = validLatencies.length
    ? +(validLatencies.reduce((a, b) => a + b, 0) / validLatencies.length).toFixed(1)
    : 0;
  const packetLoss = totalPackets > 0
    ? +((lostPackets / totalPackets) * 100).toFixed(1)
    : series.length
      ? +(series.reduce((a, b) => a + b.loss, 0) / series.length).toFixed(1)
      : 0;

  if (packetLoss >= 20 && interfaceErrors === 0) interfaceErrors = 3;

  return { avgLatency, packetLoss, interfaceErrors, series, history };
}

function extractTracerouteHops(traceReport) {
  if (!traceReport) return [];
  const rawHops = Array.isArray(traceReport)
    ? traceReport
    : traceReport.hops || traceReport.route || [];

  return rawHops.map((h, i) => {
    const ip = h.ip_address || h.ip || h.host;
    const rtt = Number(h.average_latency_ms ?? h.avg_rtt_ms ?? h.rtt_ms ?? 0);
    const noResponse = !ip || h.status === "No Response";
    return {
      hop: h.hop ?? h.hop_number ?? i + 1,
      ip: ip || "ICMP Filtered (*)",
      rtt,
      loss: noResponse ? 100 : 0
    };
  });
}

function renderRouteMap(hops, target) {
  const container = document.getElementById("routeMapContainer");
  const badge = document.getElementById("hopCountBadge");
  document.getElementById("routeSubtitle").textContent = `Active path traced to ${target}`;
  badge.textContent = `${hops.length} Hops`;

  if (!hops.length) {
    container.innerHTML = `<p class="placeholder-text">No intermediate hops returned for ${target}.</p>`;
    return;
  }

  container.innerHTML = "";
  hops.forEach((h, idx) => {
    const severity = h.loss > 0 || h.rtt > 180 ? "bad" : h.rtt > 70 ? "warn" : "";
    const node = document.createElement("div");
    node.className = `hop-node ${severity}`;
    node.innerHTML = `
      <div class="hop-num">Hop ${h.hop}</div>
      <div class="hop-ip">${h.ip}</div>
      <div class="hop-rtt">${h.rtt > 0 ? `${h.rtt} ms` : "Timeout"}</div>
    `;
    container.appendChild(node);

    if (idx < hops.length - 1) {
      const arrow = document.createElement("div");
      arrow.className = "hop-connector";
      arrow.textContent = "→";
      container.appendChild(arrow);
    }
  });
}

function updateDashboardUI({ latency, packetLoss, interfaceErrors, gatewayOk, dnsOk, analyze, series }) {
  const score = Math.max(0, Math.min(100, Math.round(100 - packetLoss * 1.5 - latency * 0.12 - interfaceErrors * 4)));
  const status = score >= 80 ? "healthy" : score >= 50 ? "degraded" : "critical";

  document.getElementById("healthScore").textContent = `${score}/100`;
  const badge = document.getElementById("statusBadge");
  badge.textContent = status;
  badge.className = `badge ${status}`;

  document.getElementById("avgLatency").textContent = `${latency} ms`;
  document.getElementById("gatewayStatus").textContent = `Gateway: ${gatewayOk ? "Reachable" : "Unreachable"}`;

  document.getElementById("packetLoss").textContent = `${packetLoss}%`;
  document.getElementById("interfaceStatus").textContent = `Interface Errors: ${interfaceErrors}`;

  const anomaly = analyze.anomaly_detection || {};
  const detected = anomaly.anomalies_detected ?? 0;
  const total = anomaly.total_records ?? 0;
  document.getElementById("anomalyCount").textContent = `${detected} / ${total}`;
  document.getElementById("dnsStatus").textContent = `DNS: ${dnsOk ? "Working" : "Failed"}`;

  const anomalyTag = document.getElementById("anomalyTag");
  const hasIssue = detected > 0 || status !== "healthy";
  anomalyTag.textContent = hasIssue ? "Anomaly Detected" : "Normal";
  anomalyTag.className = `badge ${hasIssue ? "critical" : "healthy"}`;

  // Render Root Causes from Dhruv's backend
  // Render Root Causes from Dhruv's backend
  const rca = analyze.root_cause_analysis || {};
  const causes = rca.probable_causes || rca.causes || [];
  const rcBox = document.getElementById("rootCauseList");
  if (causes.length) {
    rcBox.innerHTML = `<strong>Detected Root Causes:</strong><ul>${causes
      .map((c) =>
        typeof c === "string"
          ? `<li>${c}</li>`
          : `<li><strong>${c.cause}</strong> (${c.confidence || "High"} confidence): ${c.explanation || ""}</li>`
      )
      .join("")}</ul>`;
  } else {
    rcBox.textContent = rca.summary || "No hardware or routing anomalies detected.";
  }

  // Render Troubleshooting Recommendations from Dhruv's backend
  const ta = analyze.troubleshooting_assistant || {};
  const steps = Array.isArray(ta) ? ta : ta.recommendations || ta.steps || ta.actions || [];
  const recList = document.getElementById("recommendationsList");
  recList.innerHTML = "";
  (steps.length ? steps : ["Network metrics are within normal operating thresholds."]).forEach((s) => {
    const li = document.createElement("li");
    li.textContent = typeof s === "string" ? s : s.action || s.step || JSON.stringify(s);
    recList.appendChild(li);
  });

  renderChart(series);
}

function renderChart(series) {
  const ctx = document.getElementById("telemetryChart").getContext("2d");
  if (telemetryChart) telemetryChart.destroy();

  telemetryChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: series.map((pt) => pt.label),
      datasets: [
        {
          label: "Latency (ms)",
          data: series.map((pt) => pt.latency),
          borderColor: "#38bdf8",
          backgroundColor: "rgba(56, 189, 248, 0.15)",
          tension: 0.3,
          fill: true
        },
        {
          label: "Packet Loss (%)",
          data: series.map((pt) => pt.loss),
          borderColor: "#ef4444",
          backgroundColor: "rgba(239, 68, 68, 0.15)",
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } }
      },
      plugins: { legend: { labels: { color: "#f8fafc" } } }
    }
  });
}

function loadMockFallback(scenarioKey = "degraded") {
  const mock = MOCK_SCENARIOS[scenarioKey];
  renderRouteMap(
    [
      { hop: 1, ip: "192.168.1.1 (Local Router)", rtt: 3, loss: 0 },
      { hop: 2, ip: "10.42.0.1 (ISP Gateway)", rtt: 145, loss: 8 },
      { hop: 3, ip: "8.8.8.8 (Destination)", rtt: mock.metrics.avg_latency_ms, loss: mock.metrics.packet_loss_pct }
    ],
    mock.target
  );
  updateDashboardUI({
    latency: mock.metrics.avg_latency_ms,
    packetLoss: mock.metrics.packet_loss_pct,
    interfaceErrors: scenarioKey === "critical" ? 6 : 0,
    gatewayOk: true,
    dnsOk: scenarioKey !== "critical",
    analyze: {
      anomaly_detection: { anomalies_detected: mock.anomaly_detected ? 2 : 0, total_records: 10 },
      root_cause_analysis: { probable_causes: [mock.root_cause] },
      troubleshooting_assistant: { recommendations: mock.recommendations }
    },
    series: mock.time_series.map((t) => ({ label: t.timestamp, latency: t.latency, loss: t.loss }))
  });
}

function setLoading(isLoading) {
  document.getElementById("loader").classList.toggle("hidden", !isLoading);
}
function showError(msg) {
  const b = document.getElementById("errorBanner");
  b.textContent = msg;
  b.classList.remove("hidden");
}
function clearError() {
  document.getElementById("errorBanner").classList.add("hidden");
}