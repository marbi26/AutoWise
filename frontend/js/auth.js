// AutoWise Auth & Navigation State Controller

document.addEventListener("DOMContentLoaded", () => {
  AutoWiseAuth.initNavbar();
});

const AutoWiseAuth = {
  initNavbar() {
    const user = AutoWiseAPI.getUser();
    const navActions = document.getElementById("nav-actions");
    if (!navActions) return;

    if (user && AutoWiseAPI.getToken()) {
      // Authenticated state
      navActions.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <a href="/dashboard.html" class="btn btn-outline btn-sm">
            <span>👤 ${user.full_name || user.username}</span>
          </a>
          <button id="logout-btn" class="btn btn-secondary btn-sm" title="Log Out">Sign Out</button>
        </div>
      `;
      const logoutBtn = document.getElementById("logout-btn");
      if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
          AutoWiseAPI.logout();
        });
      }
    } else {
      // Guest state
      navActions.innerHTML = `
        <a href="/login.html" class="btn btn-outline btn-sm">Sign In</a>
        <a href="/register.html" class="btn btn-primary btn-sm">Get Started</a>
      `;
    }

    // Highlight active link in navbar
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll(".nav-links a");
    links.forEach(link => {
      const href = link.getAttribute("href");
      if (href && (href === currentPath || (currentPath === "/" && href === "/index.html"))) {
        link.classList.add("active");
      }
    });
  },

  requireAuth() {
    const token = AutoWiseAPI.getToken();
    if (!token) {
      window.location.href = `/login.html?redirect=${encodeURIComponent(window.location.pathname)}`;
      return false;
    }
    return true;
  }
};
