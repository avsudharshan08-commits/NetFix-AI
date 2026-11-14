const USE_MOCK = true; // Flip to false when integrating with Druv's Flask API
const API_BASE_URL = "http://127.0.0.1:5000/api";

let telemetryChart = null;

document.addEventListener("DOMContentLoaded", () => {
  renderDashboard(MOCK_SCENARIOS.degraded);

  document.getElementById("runDiagBtn").addEventListener("click", handleHostDiagnostic);
  document.getElementById("uploadLogBtn").addEventListener("click", handleLogUpload);
  document.getElementById("mockScenario").addEventListener("change", (e) => {
    renderDashboard(MOCK_SCENARIOS[e.target.value]);
  });
});

async function handleHostDiagnostic() {
  const host = document.getElementById("targetHost").value.trim();
  if (!host) {
    showError("Please enter a valid IP address or domain name (e.g., 8.8.8.8).");
    return;
  }

  clearError();
  setLoading(true);

  try {
    let data;
    if (USE_MOCK) {
      await simulateDelay(1200);
      const selected = document.getElementById("mockScenario").value;
      data = { ...MOCK_SCENARIOS[selected], target: host };
    } else {
      const response = await fetch(`${API_BASE_URL}/diagnose`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: host })
      });
      if (!response.ok) throw new Error("Backend diagnostic request failed.");
      data = await response.json();
    }
    renderDashboard(data);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
}

async function handleLogUpload() {
  const fileInput = document.getElementById("logFileInput");
  const file = fileInput.files[0];

  if (!file) {
    showError("Please select a .log, .txt, or .csv network diagnostic file first.");
    return;
  }

  const allowedExtensions = ["log", "txt", "csv"];
  const ext = file.name.split(".").pop().toLowerCase();
  if (!allowedExtensions.includes(ext)) {
    showError("Invalid file format. Only .log, .txt, and .csv files are supported.");
    return;
  }

  clearError();
  setLoading(true);

  try {
    let data;
    if (USE_MOCK) {
      await simulateDelay(1400);
      data = { ...MOCK_SCENARIOS.critical, target: `Uploaded: ${file.name}` };
    } else {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API_BASE_URL}/upload-log`, {
        method: "POST",
        body: formData
      });
      if (!response.ok) throw new Error("Failed to parse uploaded log file.");
      data = await response.json();
    }
    renderDashboard(data);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
}

function renderDashboard(data) {
  document.getElementById("healthScore").textContent = `${data.health_score}/100`;
  document.getElementById("avgLatency").textContent = `${data.metrics.avg_latency_ms} ms`;
  document.getElementById("packetLoss").textContent = `${data.metrics.packet_loss_pct}%`;
  document.getElementById("dnsTime").textContent = `${data.metrics.dns_resolution_ms} ms`;

  const badge = document.getElementById("statusBadge");
  badge.textContent = data.status;
  badge.className = `badge ${data.status}`;

  const anomalyTag = document.getElementById("anomalyTag");
  anomalyTag.textContent = data.anomaly_detected ? "Anomaly Detected" : "Normal";
  anomalyTag.className = `badge ${data.anomaly_detected ? "critical" : "healthy"}`;

  document.getElementById("rootCauseText").textContent = data.root_cause;

  const recList = document.getElementById("recommendationsList");
  recList.innerHTML = "";
  data.recommendations.forEach((step) => {
    const li = document.createElement("li");
    li.textContent = step;
    recList.appendChild(li);
  });

  renderChart(data.time_series);
}

function renderChart(series) {
  const ctx = document.getElementById("telemetryChart").getContext("2d");
  if (telemetryChart) telemetryChart.destroy();

  telemetryChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: series.map((pt) => pt.timestamp),
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

function setLoading(isLoading) {
  document.getElementById("loader").classList.toggle("hidden", !isLoading);
}

function showError(msg) {
  const banner = document.getElementById("errorBanner");
  banner.textContent = msg;
  banner.classList.remove("hidden");
}

function clearError() {
  document.getElementById("errorBanner").classList.add("hidden");
}

function simulateDelay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}