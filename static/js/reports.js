// reports.js - Comprehensive Charts and Analytics

// Color scheme matching the design system
const colors = {
  primary: "#34588f",
  primaryDark: "#1a3e75",
  success: "#28a745",
  warning: "#ffc107",
  danger: "#dc3545",
  info: "#17a2b8",
  light: "#f8f9fa",
  dark: "#343a40",
};

// Chart.js default configuration
Chart.defaults.font.family =
  '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
Chart.defaults.color = "#666";

// Helper function to format dates
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

// Helper function to generate gradient
function createGradient(ctx, color1, color2) {
  const gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, color1);
  gradient.addColorStop(1, color2);
  return gradient;
}

// Wait for DOM to load
document.addEventListener("DOMContentLoaded", function () {
  console.log(window.reportData);
  // 1. REVENUE TREND CHART
  const revenueCtx = document.getElementById("revenueChart");
  if (revenueCtx && window.reportData.dailyRevenue.length > 0) {
    const revenueData = window.reportData.dailyRevenue;
    const labels = revenueData.map((item) => formatDate(item.day));
    const revenues = revenueData.map((item) => parseFloat(item.revenue) || 0);
    const orders = revenueData.map((item) => item.orders);

    new Chart(revenueCtx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Revenue (DZD)",
            data: revenues,
            borderColor: colors.primary,
            backgroundColor: createGradient(
              revenueCtx.getContext("2d"),
              "rgba(52, 88, 143, 0.2)",
              "rgba(52, 88, 143, 0.05)"
            ),
            tension: 0.4,
            fill: true,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: colors.primary,
            pointBorderColor: "#fff",
            pointBorderWidth: 2,
            yAxisID: "y",
          },
          {
            label: "Orders",
            data: orders,
            borderColor: colors.success,
            backgroundColor: "rgba(40, 167, 69, 0.1)",
            tension: 0.4,
            fill: false,
            pointRadius: 3,
            pointHoverRadius: 5,
            borderDash: [5, 5],
            yAxisID: "y1",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        plugins: {
          legend: {
            display: true,
            position: "top",
            labels: {
              usePointStyle: true,
              padding: 15,
            },
          },
          tooltip: {
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            padding: 12,
            titleColor: "#fff",
            bodyColor: "#fff",
            borderColor: colors.primary,
            borderWidth: 1,
            callbacks: {
              label: function (context) {
                let label = context.dataset.label || "";
                if (label) {
                  label += ": ";
                }
                if (context.datasetIndex === 0) {
                  label +=
                    new Intl.NumberFormat("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    }).format(context.parsed.y) + " DZD";
                } else {
                  label += context.parsed.y + " orders";
                }
                return label;
              },
            },
          },
        },
        scales: {
          y: {
            type: "linear",
            display: true,
            position: "left",
            beginAtZero: true,
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
            ticks: {
              callback: function (value) {
                return value.toLocaleString() + " DZD";
              },
            },
          },
          y1: {
            type: "linear",
            display: true,
            position: "right",
            beginAtZero: true,
            grid: {
              drawOnChartArea: false,
            },
            ticks: {
              stepSize: 1,
            },
          },
          x: {
            grid: {
              display: false,
            },
          },
        },
      },
    });
  }

  // 2. REVENUE BY STATUS PIE CHART
  const revenueStatusCtx = document.getElementById("revenueStatusChart");
  if (revenueStatusCtx && window.reportData.revenueByStatus.length > 0) {
    const statusData = window.reportData.revenueByStatus;
    const statusLabels = statusData.map((item) =>
      item.status.replace(/_/g, " ").toUpperCase()
    );
    const statusRevenues = statusData.map(
      (item) => parseFloat(item.total) || 0
    );

    new Chart(revenueStatusCtx, {
      type: "doughnut",
      data: {
        labels: statusLabels,
        datasets: [
          {
            data: statusRevenues,
            backgroundColor: [
              colors.success,
              colors.primary,
              colors.info,
              colors.warning,
              colors.danger,
              "#6c757d",
            ],
            borderWidth: 2,
            borderColor: "#fff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              padding: 10,
              usePointStyle: true,
              font: {
                size: 11,
              },
            },
          },
          tooltip: {
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            padding: 12,
            callbacks: {
              label: function (context) {
                const label = context.label || "";
                const value = context.parsed;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                return (
                  label +
                  ": " +
                  value.toLocaleString() +
                  " DZD (" +
                  percentage +
                  "%)"
                );
              },
            },
          },
        },
      },
    });
  }

  // 3. CATEGORY PERFORMANCE BAR CHART
  const categoryCtx = document.getElementById("categoryChart");
  if (categoryCtx && window.reportData.categoryPerformance) {
    const categories = window.reportData.categoryPerformance;
    const categoryLabels = categories.map(
      (item) => item.product__category__name
    );
    const categoryRevenues = categories.map(
      (item) => parseFloat(item.total_revenue) || 0
    );

    new Chart(categoryCtx, {
      type: "bar",
      data: {
        labels: categoryLabels,
        datasets: [
          {
            label: "Revenue (DZD)",
            data: categoryRevenues,
            backgroundColor: colors.primary,
            borderColor: colors.primaryDark,
            borderWidth: 1,
            borderRadius: 5,
            borderSkipped: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: "y",
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            padding: 12,
            callbacks: {
              label: function (context) {
                return "Revenue: " + context.parsed.x.toLocaleString() + " DZD";
              },
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
            ticks: {
              callback: function (value) {
                return value.toLocaleString();
              },
            },
          },
          y: {
            grid: {
              display: false,
            },
          },
        },
      },
    });
  }

  // 4. USER REGISTRATION TREND
  const registrationCtx = document.getElementById("registrationChart");
  if (registrationCtx && window.reportData.userRegistrations.length > 0) {
    const regData = window.reportData.userRegistrations;
    const regLabels = regData.map((item) => formatDate(item.day));
    const regCounts = regData.map((item) => item.count);

    new Chart(registrationCtx, {
      type: "line",
      data: {
        labels: regLabels,
        datasets: [
          {
            label: "New Registrations",
            data: regCounts,
            borderColor: colors.success,
            backgroundColor: createGradient(
              registrationCtx.getContext("2d"),
              "rgba(40, 167, 69, 0.2)",
              "rgba(40, 167, 69, 0.05)"
            ),
            tension: 0.4,
            fill: true,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: colors.success,
            pointBorderColor: "#fff",
            pointBorderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: "top",
          },
          tooltip: {
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            padding: 12,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
            },
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
          },
          x: {
            grid: {
              display: false,
            },
          },
        },
      },
    });
  }

  // 5. USER TYPE DISTRIBUTION PIE CHART
  const userTypeCtx = document.getElementById("userTypeChart");
  if (userTypeCtx && window.reportData.userTypes) {
    const userTypes = window.reportData.userTypes;
    const typeLabels = userTypes.map((item) =>
      item.user_type.replace(/_/g, " ").toUpperCase()
    );
    const typeCounts = userTypes.map((item) => item.count);

    new Chart(userTypeCtx, {
      type: "doughnut",
      data: {
        labels: typeLabels,
        datasets: [
          {
            data: typeCounts,
            backgroundColor: [
              colors.primary,
              colors.success,
              colors.info,
              colors.warning,
            ],
            borderWidth: 2,
            borderColor: "#fff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              padding: 10,
              usePointStyle: true,
              font: {
                size: 11,
              },
            },
          },
          tooltip: {
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            padding: 12,
            callbacks: {
              label: function (context) {
                const label = context.label || "";
                const value = context.parsed;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                return label + ": " + value + " users (" + percentage + "%)";
              },
            },
          },
        },
      },
    });
  }

  // 6. REVIEW TREND (Volume & Rating)
  const reviewTrendCtx = document.getElementById("reviewTrendChart");
  if (reviewTrendCtx && window.reportData.reviewTrend.length > 0) {
    const reviewData = window.reportData.reviewTrend;
    const reviewLabels = reviewData.map((item) => formatDate(item.day));
    const reviewCounts = reviewData.map((item) => item.count);
    const avgRatings = reviewData.map(
      (item) => parseFloat(item.avg_rating) || 0
    );

    new Chart(reviewTrendCtx, {
      type: "bar",
      data: {
        labels: reviewLabels,
        datasets: [
          {
            label: "Review Count",
            data: reviewCounts,
            backgroundColor: colors.primary,
            borderColor: colors.primaryDark,
            borderWidth: 1,
            yAxisID: "y",
            order: 2,
          },
          {
            label: "Avg Rating",
            data: avgRatings,
            type: "line",
            borderColor: colors.warning,
            backgroundColor: "rgba(255, 193, 7, 0.1)",
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: colors.warning,
            pointBorderColor: "#fff",
            pointBorderWidth: 2,
            yAxisID: "y1",
            order: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        plugins: {
          legend: {
            display: true,
            position: "top",
            labels: {
              usePointStyle: true,
              padding: 15,
            },
          },
          tooltip: {
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            padding: 12,
          },
        },
        scales: {
          y: {
            type: "linear",
            display: true,
            position: "left",
            beginAtZero: true,
            ticks: {
              stepSize: 1,
            },
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
          },
          y1: {
            type: "linear",
            display: true,
            position: "right",
            min: 0,
            max: 5,
            ticks: {
              stepSize: 1,
              callback: function (value) {
                return value + " ★";
              },
            },
            grid: {
              drawOnChartArea: false,
            },
          },
          x: {
            grid: {
              display: false,
            },
          },
        },
      },
    });
  }

  // 7. RATING DISTRIBUTION BAR CHART
  const ratingDistCtx = document.getElementById("ratingDistChart");
  if (ratingDistCtx && window.reportData.ratingDistribution.length > 0) {
    const ratingData = window.reportData.ratingDistribution;
    const ratingLabels = ratingData.map((item) => item.rating + " Stars");
    const ratingCounts = ratingData.map((item) => item.count);

    new Chart(ratingDistCtx, {
      type: "bar",
      data: {
        labels: ratingLabels,
        datasets: [
          {
            label: "Count",
            data: ratingCounts,
            backgroundColor: [
              colors.danger,
              colors.warning,
              colors.info,
              colors.success,
              colors.primary,
            ],
            borderWidth: 0,
            borderRadius: 5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            padding: 12,
            callbacks: {
              label: function (context) {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((context.parsed.y / total) * 100).toFixed(
                  1
                );
                return context.parsed.y + " reviews (" + percentage + "%)";
              },
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
            },
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
          },
          x: {
            grid: {
              display: false,
            },
          },
        },
      },
    });
  }

  // 8. PAYMENT STATUS PIE CHART
  const paymentStatusCtx = document.getElementById("paymentStatusChart");
  if (paymentStatusCtx && window.reportData.paymentStats) {
    const paymentStats = window.reportData.paymentStats;

    new Chart(paymentStatusCtx, {
      type: "doughnut",
      data: {
        labels: ["Pending", "Verified", "Rejected"],
        datasets: [
          {
            data: [
              paymentStats.pending,
              paymentStats.verified,
              paymentStats.rejected,
            ],
            backgroundColor: [colors.warning, colors.success, colors.danger],
            borderWidth: 2,
            borderColor: "#fff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              padding: 10,
              usePointStyle: true,
              font: {
                size: 11,
              },
            },
          },
          tooltip: {
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            padding: 12,
            callbacks: {
              label: function (context) {
                const label = context.label || "";
                const value = context.parsed;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage =
                  total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                return label + ": " + value + " (" + percentage + "%)";
              },
            },
          },
        },
      },
    });
  }

  // Add animation on tab switch
  const tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
  tabLinks.forEach((link) => {
    link.addEventListener("shown.bs.tab", function () {
      // Redraw charts when tab is shown
      Chart.instances.forEach((chart) => {
        chart.resize();
      });
    });
  });
});
