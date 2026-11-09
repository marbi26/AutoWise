// AutoWise API Client

const AutoWiseAPI = {
  baseURL: "",

  getToken() {
    return localStorage.getItem("autowise_token");
  },

  setToken(token) {
    if (token) {
      localStorage.setItem("autowise_token", token);
    } else {
      localStorage.removeItem("autowise_token");
    }
  },

  getUser() {
    const raw = localStorage.getItem("autowise_user");
    try {
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  },

  setUser(user) {
    if (user) {
      localStorage.setItem("autowise_user", JSON.stringify(user));
    } else {
      localStorage.removeItem("autowise_user");
    }
  },

  async request(endpoint, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers
      });

      if (response.status === 401) {
        // Token expired or invalid
        this.setToken(null);
        this.setUser(null);
        if (window.location.pathname.includes("dashboard") || window.location.pathname.includes("profile")) {
          window.location.href = "/login.html";
        }
      }

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const errorMsg = data.detail || response.statusText || "Request failed";
        throw new Error(errorMsg);
      }
      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  },

  // Auth Endpoints
  async register(username, email, password, full_name) {
    const res = await this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, email, password, full_name })
    });
    this.setToken(res.access_token);
    this.setUser(res.user);
    return res;
  },

  async login(username, password) {
    const res = await this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password })
    });
    this.setToken(res.access_token);
    this.setUser(res.user);
    return res;
  },

  async getProfile() {
    return this.request("/api/auth/profile");
  },

  logout() {
    this.setToken(null);
    this.setUser(null);
    window.location.href = "/index.html";
  },

  // Vehicles Endpoints
  async getVehicles(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/vehicles${query ? "?" + query : ""}`);
  },

  async getVehicleDetail(vehicleId) {
    return this.request(`/api/vehicles/${vehicleId}`);
  },

  async getFilterMeta() {
    return this.request("/api/vehicles/meta/filters");
  },

  async searchVehicles(queryText) {
    return this.request(`/api/vehicles/search?q=${encodeURIComponent(queryText)}`);
  },

  // Recommendation Endpoints
  async getRecommendations(preferences) {
    return this.request("/api/recommendations", {
      method: "POST",
      body: JSON.stringify(preferences)
    });
  },

  async getRecommendationHistory() {
    return this.request("/api/recommendations/history");
  },

  async submitFeedback(vehicleId, feedbackType, rating = null, recommendationId = null) {
    return this.request("/api/recommendations/feedback", {
      method: "POST",
      body: JSON.stringify({
        vehicle_id: vehicleId,
        feedback_type: feedbackType,
        rating,
        recommendation_id: recommendationId
      })
    });
  },

  // Prediction Endpoints
  async predictCarPrice(carFeatures) {
    return this.request("/api/prediction/car", {
      method: "POST",
      body: JSON.stringify(carFeatures)
    });
  },

  async predictBikePrice(bikeFeatures) {
    return this.request("/api/prediction/bike", {
      method: "POST",
      body: JSON.stringify(bikeFeatures)
    });
  },

  async getModelMeta() {
    return this.request("/api/prediction/models-meta");
  },

  // Comparison Endpoints
  async compareVehicles(vehicleIds) {
    return this.request("/api/compare", {
      method: "POST",
      body: JSON.stringify({ vehicle_ids: vehicleIds })
    });
  },

  // Ownership Cost Endpoints
  async calculateOwnership(tcoPayload) {
    return this.request("/api/ownership/calculate", {
      method: "POST",
      body: JSON.stringify(tcoPayload)
    });
  },

  // Analytics Endpoints
  async getAnalyticsDashboard() {
    return this.request("/api/analytics/dashboard");
  },

  // Saved / Bookmarked Vehicles
  async getSavedVehicles() {
    return this.request("/api/saved-vehicles");
  },

  async saveVehicle(vehicleId) {
    return this.request(`/api/saved-vehicles/${vehicleId}`, {
      method: "POST"
    });
  },

  async removeSavedVehicle(vehicleId) {
    return this.request(`/api/saved-vehicles/${vehicleId}`, {
      method: "DELETE"
    });
  }
};
