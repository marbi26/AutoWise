// AutoWise Utilities and Helpers

const AutoWiseUtils = {
  // Format Indian Rupee currency (e.g. ₹ 8.50 Lakh or ₹ 85,000)
  formatINR(amount, formatAsLakh = false) {
    if (amount === null || amount === undefined || isNaN(amount)) return "₹ 0";
    const num = Number(amount);
    if (formatAsLakh && num >= 100000) {
      const lakhs = num / 100000;
      return `₹ ${lakhs.toFixed(2)} Lakh`;
    }
    return "₹ " + num.toLocaleString("en-IN");
  },

  // Toast notification
  showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    const icon = type === "success" ? "✓" : (type === "error" ? "✕" : "ℹ");
    toast.innerHTML = `<span style="font-weight: bold; font-size: 1.1rem;">${icon}</span> <span>${message}</span>`;
    
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  },

  // Get URL search parameters as dictionary
  getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const result = {};
    for (const [key, value] of params.entries()) {
      result[key] = value;
    }
    return result;
  },

  // Star rating HTML
  getStarsHTML(rating) {
    const stars = Math.round(Number(rating) || 0);
    let html = "";
    for (let i = 1; i <= 5; i++) {
      if (i <= stars) {
        html += '<span style="color: #fbbf24;">★</span>';
      } else {
        html += '<span style="color: #475569;">☆</span>';
      }
    }
    return html;
  }
};
