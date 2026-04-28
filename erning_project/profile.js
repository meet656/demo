const BASE_URL = 'https://demo-tn54.onrender.com';
const API_BASE = `${BASE_URL}/api`;

document.addEventListener('DOMContentLoaded', () => {
  const user = getCurrentUser();
  const token = getAuthToken();

  if (!user || !token) {
    window.location.href = 'login.html';
    return;
  }

  loadProfile(user.id);
  loadActivity(user.id);
});

async function loadProfile(userId) {
  try {
    const res = await fetch(`${API_BASE}/profile/${userId}`, {
      headers: { 'Authorization': `Bearer ${getAuthToken()}` }
    });
    
    if (res.ok) {
      const data = await res.json();
      document.getElementById('profileName').textContent = data.name;
      document.getElementById('profileEmail').textContent = data.email;
      
      const initial = data.name ? data.name.charAt(0).toUpperCase() : 'U';
      document.getElementById('profileAvatar').textContent = initial;
    } else {
      showToast('Could not load profile details', 'error');
    }
  } catch (e) {
    console.error('Error loading profile:', e);
  }
}

async function loadActivity(userId) {
  try {
    const res = await fetch(`${API_BASE}/user-activity/${userId}`, {
      headers: { 'Authorization': `Bearer ${getAuthToken()}` }
    });
    
    if (res.ok) {
      const data = await res.json();
      renderActivity(data.activities);
    } else {
      showToast('Could not load activity', 'error');
    }
  } catch (e) {
    console.error('Error loading activity:', e);
  }
}

function renderActivity(activities) {
  const container = document.getElementById('activityContainer');
  const emptyState = document.getElementById('emptyActivity');
  
  // Clear previous entries except the empty state
  Array.from(container.children).forEach(child => {
    if (child.id !== 'emptyActivity') {
      child.remove();
    }
  });

  if (!activities || activities.length === 0) {
    emptyState.style.display = 'block';
    return;
  }

  emptyState.style.display = 'none';

  activities.forEach(act => {
    const date = new Date(act.timestamp).toLocaleString();
    const typeClass = act.contact_type === 'whatsapp' ? 'badge-whatsapp' : 'badge-call';
    const typeText = act.contact_type === 'whatsapp' ? '💬 WhatsApp' : '📞 Called';
    const catIcon = getCategoryIcon(act.category);

    const div = document.createElement('div');
    div.className = 'activity-item';
    div.innerHTML = `
      <div class="activity-info">
        <h4>${catIcon} ${escapeHtml(act.service_name)}</h4>
        <p>Category: ${escapeHtml(act.category)}</p>
      </div>
      <div class="activity-meta">
        <span class="activity-badge ${typeClass}">${typeText}</span>
        <div class="activity-date">${date}</div>
      </div>
    `;
    container.appendChild(div);
  });
}
