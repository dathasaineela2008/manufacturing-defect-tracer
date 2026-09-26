/**
 * Manufacturing Defect Traceability and Prediction System (MDTPS)
 * Shared Client-Side Interactions & Helper Utilities
 */

document.addEventListener("DOMContentLoaded", () => {
  // Auto-focus first input on login or search pages
  const firstField = document.querySelector("form input:not([type=hidden]), form select");
  if (firstField && (window.location.pathname === "/login" || window.location.pathname === "/traceability")) {
    firstField.focus();
  }

  // Keyboard shortcut: Pressing '/' focuses search input if present
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
      const searchInput = document.querySelector("input[name='unit_id'], input[name='q']");
      if (searchInput) {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
    }
  });

  // Auto-dismiss success flash alerts after 6 seconds
  const successAlerts = document.querySelectorAll(".alert-success");
  successAlerts.forEach((alert) => {
    setTimeout(() => {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (err) {
        // Fallback if bootstrap object is unavailable
        alert.style.transition = "opacity 0.5s ease";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
      }
    }, 6000);
  });
});
