// AutoWise Chart.js Rendering Engine

const AutoWiseCharts = {
  // 1. Comparison Radar Chart
  renderComparisonRadar(canvasId, radarDataList) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const colors = [
      { border: "rgba(59, 130, 246, 1)", bg: "rgba(59, 130, 246, 0.25)" },
      { border: "rgba(16, 185, 129, 1)", bg: "rgba(16, 185, 129, 0.25)" },
      { border: "rgba(245, 158, 11, 1)", bg: "rgba(245, 158, 11, 0.25)" },
      { border: "rgba(244, 63, 94, 1)", bg: "rgba(244, 63, 94, 0.25)" }
    ];

    const labels = ["Performance", "Fuel Economy", "Safety", "Space & Utility", "Value for Money"];

    const datasets = radarDataList.map((item, idx) => {
      const color = colors[idx % colors.length];
      const dataPoints = labels.map(label => item.scores[label] || 0);
      return {
        label: item.vehicle_name,
        data: dataPoints,
        borderColor: color.border,
        backgroundColor: color.bg,
        borderWidth: 2,
        pointBackgroundColor: color.border,
        pointBorderColor: "#fff",
        pointHoverBackgroundColor: "#fff",
        pointHoverBorderColor: color.border
      };
    });

    return new Chart(ctx, {
      type: "radar",
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: "rgba(255, 255, 255, 0.1)" },
            grid: { color: "rgba(255, 255, 255, 0.1)" },
            pointLabels: {
              color: "#cbd5e1",
              font: { size: 12, weight: "600" }
            },
            ticks: {
              display: false,
              min: 0,
              max: 100
            }
          }
        },
        plugins: {
          legend: {
            labels: { color: "#f8fafc", font: { weight: "600" } }
          }
        }
      }
    });
  },

  // 2. Feature Importance Horizontal Bar Chart
  renderFeatureImportance(canvasId, featuresList) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const labels = featuresList.map(f => f.feature.replace("_", " ").toUpperCase());
    const data = featuresList.map(f => f.importance_percentage);

    return new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "Price Determinant Weight (%)",
          data,
          backgroundColor: "rgba(37, 99, 235, 0.7)",
          borderColor: "rgba(37, 99, 235, 1)",
          borderWidth: 1,
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: { color: "rgba(255, 255, 255, 0.08)" },
            ticks: { color: "#94a3b8" }
          },
          y: {
            grid: { display: false },
            ticks: { color: "#e2e8f0", font: { weight: "600" } }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  },

  // 3. Ownership Cost Breakdown Doughnut
  renderTCODoughnut(canvasId, summary) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const labels = ["Fuel Expenses", "Maintenance & Service", "Insurance", "Registration & Taxes", "Net Loan Interest"];
    const data = [
      summary.fuel_expense,
      summary.maintenance_and_servicing,
      summary.insurance_expense,
      summary.registration_and_taxes,
      summary.loan_interest_paid
    ];

    return new Chart(ctx, {
      type: "doughnut",
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: [
            "#3b82f6", // Blue
            "#f59e0b", // Amber
            "#10b981", // Green
            "#8b5cf6", // Purple
            "#f43f5e"  // Rose
          ],
          borderColor: "#0f172a",
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: "#cbd5e1", padding: 12, font: { size: 11 } }
          },
          tooltip: {
            callbacks: {
              label: (item) => ` ${item.label}: ₹${item.raw.toLocaleString("en-IN")}`
            }
          }
        }
      }
    });
  },

  // 4. Analytics Bar & Pie Charts
  renderBarChart(canvasId, labels, data, labelText = "Count", color = "#3b82f6") {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: labelText,
          data,
          backgroundColor: color,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { display: false }, ticks: { color: "#94a3b8" } },
          y: { grid: { color: "rgba(255, 255, 255, 0.08)" }, ticks: { color: "#94a3b8" } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  },

  renderPieChart(canvasId, labels, data, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: "pie",
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: colors || ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#06b6d4", "#f43f5e"],
          borderColor: "#111827",
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { color: "#cbd5e1" } }
        }
      }
    });
  }
};
