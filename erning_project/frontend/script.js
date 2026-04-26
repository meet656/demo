/**
 * Local Service Finder - Frontend Logic
 * =======================================
 * Handles: API calls, search/filter, category tabs,
 * rating system, favorites (localStorage), and dynamic card rendering.
 */

const API_BASE = '/api';

// --- State ---
let allServices = [];
let currentCategory = 'all';
let currentSearch = '';
let currentArea = '';
let showFavoritesOnly = false;

// Favorites stored in localStorage
function getFavorites() {
  try {
    return JSON.parse(localStorage.getItem('servicehub_favorites')) || [];
  } catch { return []; }
}
function saveFavorites(favs) {
  localStorage.setItem('servicehub_favorites', JSON.stringify(favs));
}
function toggleFavorite(id) {
  let favs = getFavorites();
  if (favs.includes(id)) {
    favs = favs.filter(f => f !== id);
    showToast('Removed from favorites', 'info');
  } else {
    favs.push(id);
    showToast('Added to favorites ❤️', 'success');
  }
  saveFavorites(favs);
  updateFavCount();
  renderServices();
}
function updateFavCount() {
  const el = document.getElementById('favCount');
  if (el) el.textContent = getFavorites().length;
}

// --- Toast Notifications ---
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  toast.innerHTML = `<span>${icons[type] || ''}</span> ${message}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(40px)';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// --- Category Icon/Emoji Helper ---
function getCategoryIcon(cat) {
  const icons = { Electrician: '⚡', Plumber: '🔧', Tutor: '📚' };
  return icons[cat] || '🔨';
}

// --- Render Star Rating HTML ---
function renderStars(rating, serviceId, interactive = true) {
  let html = '<div class="stars">';
  for (let i = 1; i <= 5; i++) {
    const filled = i <= Math.round(rating) ? 'filled' : '';
    const clickAttr = interactive ? `onclick="rateService(${serviceId}, ${i})"` : '';
    html += `<span class="star ${filled}" ${clickAttr}>★</span>`;
  }
  html += '</div>';
  return html;
}

// --- Submit Rating ---
async function rateService(serviceId, rating) {
  const token = getAuthToken();
  if (!token) {
    showToast('Please log in to submit a rating', 'error');
    setTimeout(() => window.location.href = 'login.html', 1500);
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/rate-service/${serviceId}`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ rating })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(`Rated ${rating} star${rating > 1 ? 's' : ''} — Thanks!`, 'success');
      // Update local data
      const svc = allServices.find(s => s.id === serviceId);
      if (svc) {
        svc.rating = data.new_rating;
        svc.rating_count = data.total_ratings;
      }
      renderServices();
    } else {
      showToast(data.error || 'Rating failed', 'error');
    }
  } catch {
    showToast('Could not submit rating', 'error');
  }
}

// --- Fetch Services ---
async function fetchServices() {
  showLoading(true);
  try {
    let url = `${API_BASE}/services`;
    const params = new URLSearchParams();
    if (currentSearch) params.set('search', currentSearch);
    if (currentArea) params.set('area', currentArea);
    if (currentCategory !== 'all') params.set('category', currentCategory);
    const qs = params.toString();
    if (qs) url += '?' + qs;

    const res = await fetch(url);
    if (!res.ok) throw new Error('API error');
    allServices = await res.json();
    renderServices();
  } catch (err) {
    console.error('Fetch error:', err);
    showToast('Failed to load services. Is the backend running?', 'error');
    document.getElementById('servicesGrid').innerHTML = '';
    showEmpty(true);
  } finally {
    showLoading(false);
  }
}

// --- Fetch Areas for Dropdown ---
async function fetchAreas() {
  try {
    const res = await fetch(`${API_BASE}/areas`);
    const areas = await res.json();
    const select = document.getElementById('areaFilter');
    if (!select) return;
    areas.forEach(area => {
      const opt = document.createElement('option');
      opt.value = area;
      opt.textContent = `📍 ${area}`;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error('Could not load areas:', err);
  }
}

// --- Render Service Cards ---
function renderServices() {
  const grid = document.getElementById('servicesGrid');
  if (!grid) return;

  let services = [...allServices];
  const favs = getFavorites();

  // Filter favorites if toggle is active
  if (showFavoritesOnly) {
    services = services.filter(s => favs.includes(s.id));
  }

  if (services.length === 0) {
    grid.innerHTML = '';
    showEmpty(true);
    document.getElementById('resultsCount').textContent = '0';
    return;
  }

  showEmpty(false);
  document.getElementById('resultsCount').textContent = services.length;

  grid.innerHTML = services.map((s, i) => {
    const isFav = favs.includes(s.id);
    const catLower = s.category.toLowerCase();
    const premiumClass = s.is_premium ? 'premium' : '';
    const premiumBadge = s.is_premium ? '<div class="premium-badge">⭐ Premium</div>' : '';
    const favClass = isFav ? 'favorited' : '';
    const favIcon = isFav ? '❤️' : '🤍';

    return `
      <div class="service-card ${premiumClass}" style="animation-delay: ${i * 0.05}s">
        ${premiumBadge}
        <div class="card-header">
          <div class="card-avatar ${catLower}">${getCategoryIcon(s.category)}</div>
          <div class="card-info">
            <h3>${escapeHtml(s.name)}</h3>
            <span class="card-category ${catLower}">${s.category}</span>
          </div>
        </div>
        <div class="card-details">
          <div class="detail-row">
            <span class="detail-icon">📞</span>
            <span>${s.phone}</span>
          </div>
          <div class="detail-row">
            <span class="detail-icon">📍</span>
            <span>${escapeHtml(s.location)}, ${escapeHtml(s.area)}</span>
          </div>
        </div>
        <div class="rating-section">
          ${renderStars(s.rating, s.id)}
          <span class="rating-text"><span>${s.rating}</span> (${s.rating_count} reviews)</span>
        </div>
        <div class="card-actions">
          <a href="tel:${s.phone}" class="action-btn btn-call" onclick="trackContact(${s.id}, 'call')">📞 Call Now</a>
          <a href="https://wa.me/91${s.phone}" target="_blank" class="action-btn btn-whatsapp" onclick="trackContact(${s.id}, 'whatsapp')">💬 WhatsApp</a>
          <button class="action-btn btn-favorite ${favClass}" onclick="toggleFavorite(${s.id})" title="Favorite">${favIcon}</button>
        </div>
      </div>
    `;
  }).join('');
}

// --- HTML Escaping ---
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// --- Loading / Empty States ---
function showLoading(show) {
  const el = document.getElementById('loadingState');
  if (el) el.style.display = show ? 'block' : 'none';
  const grid = document.getElementById('servicesGrid');
  if (grid && show) grid.innerHTML = '';
}
function showEmpty(show) {
  const el = document.getElementById('emptyState');
  if (el) el.style.display = show ? 'block' : 'none';
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  fetchAreas();
  fetchServices();
  updateFavCount();

  // Search
  const searchInput = document.getElementById('searchInput');
  const searchBtn = document.getElementById('searchBtn');
  let searchTimeout;

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        currentSearch = searchInput.value.trim();
        fetchServices();
      }, 400);
    });
  }
  if (searchBtn) {
    searchBtn.addEventListener('click', () => {
      currentSearch = searchInput?.value.trim() || '';
      fetchServices();
    });
  }

  // Area filter
  const areaFilter = document.getElementById('areaFilter');
  if (areaFilter) {
    areaFilter.addEventListener('change', () => {
      currentArea = areaFilter.value;
      fetchServices();
    });
  }

  // Category tabs
  const catTabs = document.getElementById('categoryTabs');
  if (catTabs) {
    catTabs.addEventListener('click', (e) => {
      const btn = e.target.closest('.cat-btn');
      if (!btn) return;
      catTabs.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentCategory = btn.dataset.category;
      fetchServices();
    });
  }

  // Favorites toggle
  const favToggle = document.getElementById('favToggle');
  if (favToggle) {
    favToggle.addEventListener('click', () => {
      showFavoritesOnly = !showFavoritesOnly;
      favToggle.classList.toggle('active', showFavoritesOnly);
      favToggle.innerHTML = showFavoritesOnly
        ? `❤️ Show All (<span id="favCount">${getFavorites().length}</span>)`
        : `❤️ Show Favorites (<span id="favCount">${getFavorites().length}</span>)`;
      renderServices();
    });
  }

  // --- Auth Form Listeners ---
  const signupForm = document.getElementById('signupForm');
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('name').value;
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const confirm = document.getElementById('confirm_password').value;

      if (password !== confirm) {
        showToast('Passwords do not match', 'error');
        return;
      }

      try {
        const res = await fetch(`${API_BASE}/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();
        if (res.ok) {
          showToast('Account created! Please log in.', 'success');
          setTimeout(() => window.location.href = 'login.html', 1500);
        } else {
          showToast(data.error || 'Signup failed', 'error');
        }
      } catch (err) {
        showToast('Connection error', 'error');
      }
    });
  }

  const loginForm = document.getElementById('userLoginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const remember = document.getElementById('remember').checked;

      try {
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, remember })
        });
        const data = await res.json();
        if (res.ok) {
          localStorage.setItem('servicehub_token', data.token);
          localStorage.setItem('servicehub_user', JSON.stringify(data.user));
          showToast('Login successful!', 'success');
          setTimeout(() => window.location.href = 'index.html', 1000);
        } else {
          showToast(data.error || 'Login failed', 'error');
        }
      } catch (err) {
        showToast('Connection error', 'error');
      }
    });
  }

  const forgotForm = document.getElementById('forgotForm');
  if (forgotForm) {
    forgotForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value;

      try {
        const res = await fetch(`${API_BASE}/auth/forgot-password`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });
        const data = await res.json();
        if (res.ok) {
          showToast('Reset token generated!', 'success');
          document.getElementById('resetTokenContainer').style.display = 'block';
          document.getElementById('resetTokenDisplay').textContent = data.reset_token;
        } else {
          showToast(data.error || 'Email not found', 'error');
        }
      } catch (err) {
        showToast('Connection error', 'error');
      }
    });
  }

  const resetForm = document.getElementById('resetForm');
  if (resetForm) {
    resetForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const token = document.getElementById('token').value;
      const password = document.getElementById('password').value;

      try {
        const res = await fetch(`${API_BASE}/auth/reset-password`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token, password })
        });
        const data = await res.json();
        if (res.ok) {
          showToast('Password reset successfully!', 'success');
          setTimeout(() => window.location.href = 'login.html', 1500);
        } else {
          showToast(data.error || 'Reset failed', 'error');
        }
      } catch (err) {
        showToast('Connection error', 'error');
      }
    });
  }
});

// --- Auth Helpers ---
function getAuthToken() {
  return localStorage.getItem('servicehub_token');
}

function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem('servicehub_user'));
  } catch { return null; }
}

async function logoutUser() {
  const token = getAuthToken();
  if (token) {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
    } catch (e) { console.error('Logout error', e); }
  }
  localStorage.removeItem('servicehub_token');
  localStorage.removeItem('servicehub_user');
  window.location.href = 'index.html';
}

function initNavbar() {
  const navLinks = document.getElementById('navLinks');
  if (!navLinks) return;

  const user = getCurrentUser();
  const token = getAuthToken();

  let html = `<a href="index.html" class="nav-link active" id="nav-home">Home</a>`;

  if (user && token) {
    const initial = user.name ? user.name.charAt(0).toUpperCase() : 'U';
    html += `
      <div class="user-dropdown">
        <button class="user-menu-btn" onclick="window.location.href='profile.html'">
          <div class="user-avatar">${initial}</div>
          ${escapeHtml(user.name.split(' ')[0])}
        </button>
      </div>
      <a href="#" class="nav-link" onclick="logoutUser(); return false;">Logout</a>
    `;
    
    // Only show Admin button if the user has the admin role
    if (user.role === 'admin') {
      html += `<a href="admin.html" class="nav-link admin-link" id="nav-admin">⚙ Admin</a>`;
    }
  } else {
    html += `
      <a href="login.html" class="nav-link">Log In</a>
      <a href="signup.html" class="nav-link" style="font-weight: 600; color: var(--accent-primary);">Sign Up</a>
    `;
  }
  
  navLinks.innerHTML = html;
}

// --- Tracking ---
async function trackContact(serviceId, type) {
  const token = getAuthToken();
  if (!token) return; // Only track logged in users

  try {
    await fetch(`${API_BASE}/track-contact`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        service_id: serviceId,
        contact_type: type
      })
    });
  } catch (e) {
    console.error('Failed to track contact:', e);
  }
}
