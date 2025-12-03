// DOM Ready: consolidated
document.addEventListener('DOMContentLoaded', function () {
    // 🔹 Sidebar Toggle (for mobile)
    const sidebarToggle = document.getElementById('sidebarToggle');
    const nav = document.getElementById('nav');

    if (sidebarToggle && nav) {
        sidebarToggle.addEventListener('click', () => {
            nav.classList.toggle('active');
        });

        // Close sidebar when clicking a nav link (mobile)
        document.querySelectorAll('.nav a').forEach(link => {
            link.addEventListener('click', () => {
                nav.classList.remove('active');
            });
        });
    }

    // 🔹 Optional: Confirm logout (improves UX)
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function (e) {
            // no-op placeholder or confirm if you want
        });
    }

    // 🔹 Password toggle (if present on login/signup)
    const toggleButtons = document.querySelectorAll('.password-text-toggle');
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const wrapper = this.closest('.password-wrapper');
            if (!wrapper) return;
            const input = wrapper.querySelector('input');
            if (!input) return;
            if (input.type === 'password') {
                input.type = 'text';
                this.textContent = 'Hide';
            } else {
                input.type = 'password';
                this.textContent = 'Show';
            }
        });
    });

    // Search button handler (if present)
    const searchBtn = document.getElementById("searchBtn");
    if (searchBtn) {
        searchBtn.addEventListener("click", () => {
            const input = document.getElementById("searchInput");
            const query = input ? input.value.trim() : "";
            let url = "/my-shipments";
            if (query !== "") {
                url += `?shipment=${encodeURIComponent(query)}`;
            }
            window.location.href = url;
        });
    }

    // View Stream: Intercept device selection & load stream without full reload
    const streamForm = document.querySelector('.stream-controls form');
    const deviceSelect = document.getElementById('deviceSelect') || document.getElementById('device-select');
    if (streamForm && deviceSelect) {
        streamForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const device = deviceSelect.value;
            const url = new URL('/view-stream', window.location.origin);
            if (device) url.searchParams.set('device', device);

            try {
                const response = await fetch(url, { headers: { 'Accept': 'text/html' } });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const html = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newStreamContainer = doc.getElementById('streamContainer');
                const currentStreamContainer = document.getElementById('streamContainer');
                if (newStreamContainer && currentStreamContainer) {
                    currentStreamContainer.outerHTML = newStreamContainer.outerHTML;
                }
                window.history.replaceState(null, '', url);
            } catch (err) {
                console.error('Failed to refresh stream:', err);
                alert('Failed to load stream. Please try again.');
            }
        });
    }

    // If there's a device-select dropdown (not inside form) load on change
    if (deviceSelect) {
        deviceSelect.addEventListener('change', (e) => {
            const val = e.target.value;
            if (val) loadStream(val).catch(err => console.error(err));
        });
    }
});

// fetch stream data and populate table
async function loadStream(deviceId) {
    try {
        const response = await fetch(`/api/stream/${encodeURIComponent(deviceId)}`);
        if (!response.ok) {
            throw new Error('Failed to fetch stream data: ' + response.status);
        }
        const data = await response.json();
        const tableBody = document.getElementById('stream-table-body');
        if (!tableBody) {
            alert("Stream table not found on this page.");
            return;
        }
        tableBody.innerHTML = '';
        if (data.stream_data && data.stream_data.length > 0) {
            data.stream_data.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.timestamp || ''}</td>
                    <td>${item.Battery_Level || ''}</td>
                    <td>${item.First_Sensor_temperature || ''}</td>
                    <td>${(item.Route_From || '')} → ${(item.Route_To || '')}</td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="4" style="text-align:center">No data found for this device.</td>`;
            tableBody.appendChild(row);
        }
    } catch (err) {
        console.error('loadStream error:', err);
        alert('Error loading stream data.');
    }
}

// Optional: refresh devices table (call refreshDevices() somewhere if you want periodic updates)
function refreshDevices() {
    fetch('/devices')
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newTable = doc.querySelector('#devicesTable tbody');
            const current = document.querySelector('#devicesTable tbody');
            if (newTable && current) {
                current.replaceWith(newTable);
            }
        })
        .catch(err => console.error('Refresh failed:', err));
}
