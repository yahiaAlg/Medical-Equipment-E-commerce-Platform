// Profile Page Tab Functionality
document.addEventListener("DOMContentLoaded", function () {
  const tabs = document.querySelectorAll(".profile-tab");
  const tabPanes = document.querySelectorAll(".tab-pane");

  // Handle tab switching
  tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const targetId = this.getAttribute("data-tab");

      // Remove active class from all tabs and panes
      tabs.forEach((t) => t.classList.remove("active"));
      tabPanes.forEach((pane) => pane.classList.remove("active"));

      // Add active class to clicked tab and corresponding pane
      this.classList.add("active");
      document.getElementById(targetId).classList.add("active");

      // Store active tab in sessionStorage
      sessionStorage.setItem("activeProfileTab", targetId);
    });
  });

  // Restore active tab from sessionStorage or URL hash
  const savedTab = sessionStorage.getItem("activeProfileTab");
  const urlHash = window.location.hash.substring(1);

  if (urlHash && document.getElementById(urlHash)) {
    activateTab(urlHash);
  } else if (savedTab && document.getElementById(savedTab)) {
    activateTab(savedTab);
  }

  // Check if there are password form errors and switch to that tab
  const passwordErrors = document.querySelector(
    "#change-password .error-message"
  );
  if (passwordErrors) {
    activateTab("change-password");
  }

  function activateTab(tabId) {
    tabs.forEach((t) => t.classList.remove("active"));
    tabPanes.forEach((pane) => pane.classList.remove("active"));

    const targetTab = document.querySelector(`[data-tab="${tabId}"]`);
    const targetPane = document.getElementById(tabId);

    if (targetTab && targetPane) {
      targetTab.classList.add("active");
      targetPane.classList.add("active");
    }
  }

  // Password strength indicator (optional enhancement)
  const newPasswordInput = document.querySelector(
    'input[name="new_password1"]'
  );
  if (newPasswordInput) {
    newPasswordInput.addEventListener("input", function () {
      // You can add password strength indicator here if desired
    });
  }

  // Smooth scroll to error messages
  const errorMessages = document.querySelectorAll(".error-message");
  if (errorMessages.length > 0) {
    errorMessages[0].scrollIntoView({ behavior: "smooth", block: "center" });
  }

  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
});
