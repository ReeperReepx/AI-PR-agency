/**
 * Editorial PR Matchmaking Platform
 * Frontend JavaScript for API interactions and UI management
 */

// API Configuration
const API_BASE = '';

// State management
const state = {
  user: null,
  token: localStorage.getItem('auth_token'),
  loading: false,
};

// Utility functions
const api = {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(state.token && { Authorization: `Bearer ${state.token}` }),
      ...options.headers,
    };

    try {
      state.loading = true;
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    } finally {
      state.loading = false;
    }
  },

  get(endpoint) {
    return this.request(endpoint);
  },

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  },
};

// Auth functions
const auth = {
  async login(email, password) {
    const response = await api.post('/auth/login', { email, password });
    state.token = response.access_token;
    localStorage.setItem('auth_token', response.access_token);
    return response;
  },

  async register(email, password, userType) {
    const response = await api.post('/auth/register', {
      email,
      password,
      user_type: userType,
    });
    return response;
  },

  logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  },

  isAuthenticated() {
    return !!state.token;
  },
};

// User functions
const users = {
  async getMe() {
    const response = await api.get('/users/me');
    state.user = response;
    return response;
  },
};

// Match functions
const matches = {
  async findJournalists(page = 1, pageSize = 20) {
    return api.get(`/matching/journalists?page=${page}&page_size=${pageSize}`);
  },

  async findCompanies(page = 1, pageSize = 20) {
    return api.get(`/matching/companies?page=${page}&page_size=${pageSize}`);
  },

  async getSimilarJournalists(limit = 10) {
    return api.get(`/matching/similar-journalists?limit=${limit}`);
  },

  async getSimilarCompanies(limit = 10) {
    return api.get(`/matching/similar-companies?limit=${limit}`);
  },

  async getJournalistInsights(journalistId) {
    return api.get(`/matching/journalists/${journalistId}/insights`);
  },

  async getCompanyInsights(companyId) {
    return api.get(`/matching/companies/${companyId}/insights`);
  },
};

// Feedback functions
const feedback = {
  async submit(data) {
    return api.post('/feedback/', data);
  },

  async getMine() {
    return api.get('/feedback/me');
  },
};

// Analytics functions
const analytics = {
  async getMyMetrics() {
    return api.get('/analytics/me');
  },

  async getPlatformMetrics() {
    return api.get('/analytics/platform');
  },
};

// Profile functions
const profiles = {
  async getJournalistProfile() {
    return api.get('/journalists/me');
  },

  async createJournalistProfile(data) {
    return api.post('/journalists/me', data);
  },

  async updateJournalistProfile(data) {
    return api.put('/journalists/me', data);
  },

  async getCompanyProfile() {
    return api.get('/companies/me');
  },

  async createCompanyProfile(data) {
    return api.post('/companies/me', data);
  },

  async updateCompanyProfile(data) {
    return api.put('/companies/me', data);
  },
};

// Topics functions
const topics = {
  async list(category = null) {
    const params = category ? `?category=${category}` : '';
    return api.get(`/topics/${params}`);
  },
};

// UI Helpers
const ui = {
  showLoading(element) {
    element.classList.add('loading');
    element.innerHTML = '<div class="skeleton skeleton-text"></div>';
  },

  hideLoading(element) {
    element.classList.remove('loading');
  },

  showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        ${type === 'success' ? '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>' : ''}
        ${type === 'error' ? '<circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>' : ''}
        ${type === 'warning' ? '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>' : ''}
        ${type === 'info' ? '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line>' : ''}
      </svg>
      <span>${message}</span>
    `;

    document.body.appendChild(alert);
    alert.style.position = 'fixed';
    alert.style.top = '20px';
    alert.style.right = '20px';
    alert.style.zIndex = '9999';
    alert.style.animation = 'slideIn 0.3s ease';

    setTimeout(() => {
      alert.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => alert.remove(), 300);
    }, 3000);
  },

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  },

  getInitials(name) {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  },

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
};

// Modal management
const modal = {
  open(modalId) {
    const modalEl = document.getElementById(modalId);
    if (modalEl) {
      modalEl.classList.add('active');
    }
  },

  close(modalId) {
    const modalEl = document.getElementById(modalId);
    if (modalEl) {
      modalEl.classList.remove('active');
    }
  },

  closeAll() {
    document.querySelectorAll('.modal-overlay').forEach((m) => {
      m.classList.remove('active');
    });
  },
};

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
  // Close modal on overlay click
  document.querySelectorAll('.modal-overlay').forEach((overlay) => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.classList.remove('active');
      }
    });
  });

  // Close modal on ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      modal.closeAll();
    }
  });

  // Handle navigation active state
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach((item) => {
    if (item.getAttribute('href') === currentPath) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Initialize sync indicator
  updateSyncStatus();
});

// Sync status updater
function updateSyncStatus() {
  const syncIndicator = document.querySelector('.sync-indicator span:last-child');
  if (syncIndicator) {
    const updateTime = () => {
      syncIndicator.textContent = 'Synced just now';
    };
    setInterval(updateTime, 30000);
  }
}

// Animation keyframes (add to head)
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(style);

// Export for use in templates
window.app = {
  api,
  auth,
  users,
  matches,
  feedback,
  analytics,
  profiles,
  topics,
  ui,
  modal,
  state,
};
