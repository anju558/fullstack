// Single app script: site-wide behaviors + index-specific handling
document.addEventListener('DOMContentLoaded', () => {
  // Mobile nav toggle
  const navToggle = document.getElementById('navToggle');
  const nav = document.getElementById('nav');
  if (navToggle && nav) navToggle.addEventListener('click', () => nav.classList.toggle('show'));

  // Sidebar toggle for mobile
  const sidebarToggle = document.getElementById('sidebarToggle');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      const sidebarNav = document.querySelector('.sidebar-nav');
      if (sidebarNav) sidebarNav.classList.toggle('show');
    });
  }

  // Smooth scrolling for internal links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const href = a.getAttribute('href');
      if (!href || href === '#') return;
      e.preventDefault();
      const el = document.querySelector(href);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // Close modals when clicking outside
  const modals = document.querySelectorAll('.modal');
  modals.forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.style.display = 'none';
    });
  });

  // Basic form validation (applies to all forms)
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function (e) {
      // Skip client-side blocking for forms that expect JS handling elsewhere
      const requiredFields = form.querySelectorAll('[required]');
      let isValid = true;

      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          field.style.borderColor = '#ef4444';
          field.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.08)';
        } else {
          field.style.borderColor = 'rgba(255,255,255,0.06)';
          field.style.boxShadow = 'none';
        }
      });

      if (!isValid) {
        e.preventDefault();
        alert('❌ Please fill in all required fields');
        return false;
      }
    });
  });

  // Close buttons for modals
  document.querySelectorAll('.modal-close, #closeModal').forEach(btn => {
    if (btn) btn.addEventListener('click', function () {
      const modal = this.closest('.modal');
      if (modal) modal.style.display = 'none';
    });
  });

  // Cancel buttons
  document.querySelectorAll('#cancelModal').forEach(btn => {
    if (btn) btn.addEventListener('click', function () {
      const modal = this.closest('.modal');
      if (modal) modal.style.display = 'none';
    });
  });

  // Index page: login handler (only run on site root/index)
  const path = window.location.pathname.replace(/\/+$/, '');
  if (path === '' || path === '/' || path.endsWith('/index.html')) {
    document.addEventListener('submit', async (e) => {
      if (!e.target.matches('form')) return;
      e.preventDefault();

      const email = document.querySelector('#email')?.value?.trim() || 'test@example.com';
      const password = document.querySelector('#password')?.value || '123456';

      try {
        const res = await fetch('http://127.0.0.1:8000/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          credentials: 'include',
          body: new URLSearchParams({ username: email, password })
        });

        if (!res.ok) throw new Error('Server responded ' + res.status);
        console.log('✅ Login success');
        setTimeout(() => { window.location.href = '/dashboard'; }, 400);
      } catch (err) {
        console.error('❌ Fetch failed:', err);
        alert('⚠️ Unable to connect to the server. Make sure the backend is running on http://127.0.0.1:8000');
      }
    });
  }

  // Input error clearing
  document.querySelectorAll('input[type="password"], input[type="email"], input[type="text"]').forEach(input => {
    input.addEventListener('input', function () {
      this.style.borderColor = 'rgba(255,255,255,0.06)';
      this.style.boxShadow = 'none';
      const errorElement = this.parentElement?.querySelector('.error');
      if (errorElement) errorElement.textContent = '';
    });
  });

  console.log('✅ App initialized successfully');

  // ===== My Shipments Page Handler =====
  const shipmentsContainer = document.getElementById('shipmentsContainer');
  if (shipmentsContainer) {
    loadMyShipments();
  }

  // ===== View Stream Page Handler =====
  const deviceSelect = document.getElementById('deviceSelect');
  const streamContainer = document.getElementById('streamContainer');
  if (deviceSelect && streamContainer) {
    loadDevicesForStream();
    deviceSelect.addEventListener('change', pollStream);
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
      loadDevicesForStream();
      if (deviceSelect.value) pollStream();
    });
  }
});

// Load user's shipments from API
async function loadMyShipments() {
  try {
    const res = await fetch('/api/my-shipments');
    if (!res.ok) throw new Error('Failed to fetch shipments');
    const data = await res.json();
    const container = document.getElementById('shipmentsContainer');
    
    if (!data.shipments || data.shipments.length === 0) {
      container.innerHTML = '<p class="empty-state">No shipments yet. <a href="/create-shipment">Create one now</a></p>';
      return;
    }

    const html = data.shipments.map((s, idx) => `
      <div class="shipment-card">
        <div class="shipment-header">
          <h3>${s.Shipment_Number || 'N/A'}</h3>
          <span class="shipment-date">${new Date(s.created_at).toLocaleDateString()}</span>
        </div>
        <div class="shipment-details">
          <p><strong>Route:</strong> ${s.Route_Details || 'N/A'}</p>
          <p><strong>Device:</strong> ${s.Device || 'N/A'}</p>
          <p><strong>Status:</strong> ${s.Status || 'Pending'}</p>
          <p><strong>Expected Delivery:</strong> ${s.Expected_Delivery_Date || 'N/A'}</p>
          <p><strong>Description:</strong> ${s.Shipment_Description || 'N/A'}</p>
        </div>
      </div>
    `).join('');
    
    container.innerHTML = html;
  } catch (err) {
    console.error('Error loading shipments:', err);
    document.getElementById('shipmentsContainer').innerHTML = `<p class="error">Error loading shipments: ${err.message}</p>`;
  }
}

// Load devices for stream page
async function loadDevicesForStream() {
  try {
    const res = await fetch('/api/devices');
    if (!res.ok) throw new Error('Failed to load devices');
    const data = await res.json();
    const deviceSelect = document.getElementById('deviceSelect');
    const devices = Array.from(new Set(data.devices.map(d => d.Device).filter(Boolean)));
    
    // Preserve selected value
    const currentValue = deviceSelect.value;
    deviceSelect.innerHTML = '<option value="">-- All Devices --</option>';
    devices.forEach(dev => {
      const opt = document.createElement('option');
      opt.value = dev;
      opt.textContent = dev;
      deviceSelect.appendChild(opt);
    });
    
    if (currentValue) deviceSelect.value = currentValue;
  } catch (err) {
    console.error('Error loading devices:', err);
  }
}

// Poll and update stream
let streamPollInterval = null;
async function pollStream() {
  if (streamPollInterval) clearInterval(streamPollInterval);
  
  const streamArea = document.querySelector('.stream-area');
  const selectedDevice = document.getElementById('deviceSelect')?.value || null;
  
  const updateStream = async () => {
    try {
      const res = await fetch('/api/devices');
      if (!res.ok) return;
      const data = await res.json();
      
      let filtered = data.devices || [];
      if (selectedDevice) {
        filtered = filtered.filter(d => d.Device === selectedDevice);
      }
      
      if (!filtered.length) {
        streamArea.textContent = 'No data available.';
        return;
      }
      
      // Show latest entry
      const latest = filtered[filtered.length - 1];
      streamArea.textContent = JSON.stringify(latest, null, 2);
    } catch (err) {
      console.error('Stream poll error:', err);
    }
  };
  
  // Initial update
  updateStream();
  // Then poll every 3 seconds
  streamPollInterval = setInterval(updateStream, 3000);
}


