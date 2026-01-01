// Dashboard JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // Animate stat numbers on page load
  animateStats();

  // Animate progress bars
  animateProgressBars();

  // Auto-dismiss alerts after 5 seconds
  autoCloseAlerts();

  // Initialize tooltips if Bootstrap is loaded
  if (typeof bootstrap !== "undefined") {
    initTooltips();
  }
});

// Counter animation for stats
function animateStats() {
  const statNumbers = document.querySelectorAll(
    ".dashboard-card h3, .activity-icon + h4"
  );

  statNumbers.forEach((stat) => {
    const text = stat.textContent.trim();
    const number = parseInt(text.replace(/[^0-9]/g, ""));

    if (!isNaN(number) && number > 0) {
      animateValue(stat, 0, number, 1000, text);
    }
  });
}

function animateValue(element, start, end, duration, originalText) {
  const prefix = originalText.replace(/[0-9]/g, "").trim();
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Easing function
    const easeOutQuad = progress * (2 - progress);
    const current = Math.floor(start + (end - start) * easeOutQuad);

    element.textContent = prefix ? `${prefix}${current}` : current;

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      element.textContent = originalText;
    }
  }

  requestAnimationFrame(update);
}

// Animate progress bars
function animateProgressBars() {
  const progressBars = document.querySelectorAll(".progress-bar");

  progressBars.forEach((bar) => {
    const width = bar.style.width;
    bar.style.width = "0";

    setTimeout(() => {
      bar.style.width = width;
    }, 100);
  });
}

// Auto-close alerts
function autoCloseAlerts() {
  const alerts = document.querySelectorAll(".alert:not(.alert-permanent)");

  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
}

// Initialize Bootstrap tooltips
function initTooltips() {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

// Add loading state to buttons
document.querySelectorAll("form").forEach((form) => {
  form.addEventListener("submit", function (e) {
    const submitBtn = this.querySelector('button[type="submit"]');
    if (submitBtn && !submitBtn.disabled) {
      submitBtn.disabled = true;
      const originalText = submitBtn.innerHTML;
      submitBtn.innerHTML =
        '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';

      // Re-enable after 5 seconds as fallback
      setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }, 5000);
    }
  });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

// Add fade-in animation to cards
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px",
};

const observer = new IntersectionObserver(function (entries) {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = "0";
      entry.target.style.transform = "translateY(20px)";

      setTimeout(() => {
        entry.target.style.transition =
          "opacity 0.5s ease, transform 0.5s ease";
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }, 100);

      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll(".card").forEach((card) => {
  observer.observe(card);
});

// Confirmation for logout and critical actions
document.querySelectorAll('form[action*="logout"]').forEach((form) => {
  form.addEventListener("submit", function (e) {
    if (!confirm("Are you sure you want to logout?")) {
      e.preventDefault();
    }
  });
});

// Real-time search filter for tables (if needed)
const searchInputs = document.querySelectorAll("input[data-table-search]");
searchInputs.forEach((input) => {
  const tableId = input.getAttribute("data-table-search");
  const table = document.getElementById(tableId);

  if (table) {
    input.addEventListener("keyup", function () {
      const filter = this.value.toLowerCase();
      const rows = table.querySelectorAll("tbody tr");

      rows.forEach((row) => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? "" : "none";
      });
    });
  }
});
