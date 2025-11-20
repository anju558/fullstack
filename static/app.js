/**
 * ============================================
 * SHIPTRACK APP - CLEAN JAVASCRIPT
 * ============================================
 * Well-organized with clear sections
 * API endpoints: /api/profile, /api/my-shipments, /api/devices
 */

// ================== INITIALIZATION ==================
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ Initializing app...');
  initMobileNav();
  initForms();
  initModals();
  initPageHandlers();
});

// ================== NAVIGATION & UI SETUP ==================

function initMobileNav() {
  const sidebarToggle = document.getElementById('sidebarToggle');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      const nav = document.querySelector('.sidebar-nav');
      if (nav) nav.classList.toggle('show');
    });
  }
}

function initForms() {
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', validateForm);
  });
  
  document.querySelectorAll('input, textarea').forEach(input => {
    input.addEventListener('input', clearInputError);
  });
}

function validateForm(e) {
  const fields = this.querySelectorAll('[required]');
  let valid = true;
  
  fields.forEach(field => {
    if (!field.value.trim()) {
      valid = false;
      showInputError(field);
    }
  });
  
  if (!valid) e.preventDefault();
}

function showInputError(input) {
  input.style.borderColor = '#ef4444';
  input.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.08)';
}

function clearInputError() {
  this.style.borderColor = 'rgba(255,255,255,0.06)';
  this.style.boxShadow = 'none';
}

function initModals() {
  document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal(modal);
    });
  });
  
  document.querySelectorAll('.modal-close, #closeModal').forEach(btn => {
    btn.addEventListener('click', function() {
      closeModal(this.closest('.modal'));
    });
  });
  
  document.querySelectorAll('#cancelModal').forEach(btn => {
    btn.addEventListener('click', function() {
      closeModal(this.closest('.modal'));
    });
  });
}

function closeModal(modal) {
  if (modal) modal.style.display = 'none';
}

function initPageHandlers() {
  if (document.getElementById('profileContent')) loadUserProfile();
  if (document.getElementById('shipmentsContainer')) loadMyShipments();
  if (document.getElementById('deviceSelect')) {
    loadDevicesForStream();
    document.getElementById('deviceSelect').addEventListener('change', pollStream);
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
      loadDevicesForStream();
      if (document.getElementById('deviceSelect').value) pollStream();
    });
  }
}

// ================== PROFILE PAGE ==================
// API ENDPOINT: /api/profile
async function loadUserProfile() {
  const content = document.getElementById('profileContent');
  
  try {
    content.innerHTML = '<p class="loading">⏳ Loading profile...</p>';
    
    const res = await fetch('/api/profile');
    if (res.status === 401) {
      window.location.href = '/login';
      return;
    }
    if (!res.ok) throw new Error(`Error ${res.status}`);
    
    const data = await res.json();
    
    content.innerHTML = `
      <div class="profile-field">
        <span class="profile-label">Username</span>
        <span class="profile-value">${escapeHtml(data.username)}</span>
      </div>
      <div class="profile-field">
        <span class="profile-label">Email</span>
        <span class="profile-value">${escapeHtml(data.email)}</span>
      </div>
      <div class="profile-field">
        <span class="profile-label">User ID</span>
        <span class="profile-value">${escapeHtml(data.id)}</span>
      </div>
      <div class="profile-field">
        <span class="profile-label">Member Since</span>
        <span class="profile-value">${formatDate(data.created_at)}</span>
      </div>
    `;
    console.log('✅ Profile loaded');
  } catch (err) {
    console.error('Profile error:', err);
    content.innerHTML = `<div class="error">❌ ${escapeHtml(err.message)}</div>`;
  }
}

// ================== SHIPMENTS PAGE ==================
// API ENDPOINT: /api/my-shipments
async function loadMyShipments() {
  try {
    const res = await fetch('/api/my-shipments');
    if (!res.ok) throw new Error('Failed to load');
    
    const data = await res.json();
    const container = document.getElementById('shipmentsContainer');
    
    if (!data.shipments || !data.shipments.length) {
      container.innerHTML = '<p class="empty-state">📦 No shipments. <a href="/create-shipment">Create one</a></p>';
      return;
    }
    
    container.innerHTML = data.shipments.map(s => `
      <div class="shipment-card">
        <div class="shipment-header">
          <h3>${escapeHtml(s.Shipment_Number || 'N/A')}</h3>
          <span class="shipment-date">${formatDate(s.created_at)}</span>
        </div>
        <div class="shipment-details">
          <p><strong>Route:</strong> ${escapeHtml(s.Route_Details || 'N/A')}</p>
          <p><strong>Device:</strong> ${escapeHtml(s.Device || 'N/A')}</p>
          <p><strong>Delivery:</strong> ${escapeHtml(s.Expected_Delivery_Date || 'N/A')}</p>
          <p><strong>Description:</strong> ${escapeHtml(s.Shipment_Description || 'N/A')}</p>
        </div>
      </div>
    `).join('');
    
    console.log('✅ Shipments loaded');
  } catch (err) {
    document.getElementById('shipmentsContainer').innerHTML = '<p class="error">Error loading shipments</p>';
  }
}

// ================== DEVICE STREAM ==================
// API ENDPOINT: /api/devices
let streamPollInterval = null;

async function loadDevicesForStream() {
  try {
    const res = await fetch('/api/devices');
    if (!res.ok) throw new Error('Failed to load');
    
    const data = await res.json();
    const select = document.getElementById('deviceSelect');
    const devices = Array.from(new Set(data.devices.map(d => d.Device).filter(Boolean)));
    
    const current = select.value;
    select.innerHTML = '<option value="">-- All Devices --</option>';
    
    devices.forEach(dev => {
      const opt = document.createElement('option');
      opt.value = dev;
      opt.textContent = dev;
      select.appendChild(opt);
    });
    
    if (current) select.value = current;
  } catch (err) {
    console.error('Device load error:', err);
  }
}

async function pollStream() {
  if (streamPollInterval) clearInterval(streamPollInterval);
  
  const area = document.querySelector('.stream-area');
  const device = document.getElementById('deviceSelect')?.value || null;
  
  const update = async () => {
    try {
      const res = await fetch('/api/devices');
      if (!res.ok) return;
      
      const data = await res.json();
      let items = data.devices || [];
      
      if (device) items = items.filter(d => d.Device === device);
      
      if (!items.length) {
        area.textContent = '⏳ No data available';
        return;
      }
      
      area.textContent = JSON.stringify(items[items.length - 1], null, 2);
    } catch (err) {
      console.error('Stream error:', err);
    }
  };
  
  await update();
  streamPollInterval = setInterval(update, 3000);
}

// ================== UTILITY FUNCTIONS ==================

function escapeHtml(text) {
  if (!text) return '';
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

function formatDate(iso) {
  if (!iso) return 'N/A';
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return iso;
  }
}


