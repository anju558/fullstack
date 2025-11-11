# ShipTrack — Frontend Setup & Usage Guide

## Files Created

### Pages
1. **index.html** — Landing page with features, pricing, and CTAs
2. **signup.html** — Registration page with form validation and password strength meter
3. **login.html** — Login page with JWT-based authentication
4. **dashboard.html** — Shipments management with table, filters, and create modal
5. **devices.html** — Device tracking with status, battery, location, and analytics

### Styling & Scripts
- **styles.css** — Complete styling for all pages (auth, dashboard, responsive)
- **app.js** — Mobile nav toggle, smooth scroll, auth checks, modal close handlers

## Quick Start

### Prerequisites
- Backend running on `http://127.0.0.1:8000` (FastAPI with MongoDB)
- Frontend served on `http://127.0.0.1:5500` or similar

### Step 1: Start the Backend
```powershell
cd c:\Users\anjal\OneDrive\Desktop\project\fullstack\backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Step 2: Serve the Frontend
```powershell
cd c:\Users\anjal\OneDrive\Desktop\project\fullstack\frontend
python -m http.server 5500
```

### Step 3: Open in Browser
Navigate to `http://127.0.0.1:5500/index.html`

## Features

### Authentication Flow
1. **Signup** (`signup.html`)
   - Username (4+ chars), email, password with strength meter
   - Password requirements: 8+ chars, uppercase, lowercase, number, special char
   - Submits to `POST /signup` endpoint
   - Redirects to login on success

2. **Login** (`login.html`)
   - Email and password
   - Submits to `POST /login` endpoint (OAuth2 PasswordRequestForm)
   - Stores JWT token in `localStorage`
   - Redirects to dashboard

3. **Protected Pages**
   - Dashboard & Devices check for token on load
   - Redirect to login if not authenticated

### Dashboard (Shipments)
- **View Shipments**: Table with shipment details (number, route, device, status, delivery date)
- **Search & Filter**: By shipment name or status
- **Create Shipment**: Modal form with all shipment fields
- **Mock Data**: Demo shipments preloaded (update to call backend API)

### Devices Page
- **Device Cards**: Status (online/offline), location, battery, last update, active shipments
- **Analytics**: Summary stats (active devices, offline count, avg battery, total tracked)
- **Visual Indicators**: Progress bars for battery, color-coded badges for status

## API Integration Notes

### Endpoints Used
- `POST /signup?username=...&email=...&password=...&confirm_password=...`
- `POST /login` (form-urlencoded with username, password)
- `POST /shipments` (create new shipment, requires Bearer token)
- `GET /shipments` (get shipment list — not yet integrated)

### Token Management
- Stored in `localStorage` as `access_token`
- Sent in Authorization header as `Bearer {token}`

### CORS Configuration
If frontend and backend run on different origins, add CORS middleware to `backend/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Customization

### Change API Base URL
Edit the `API_BASE` variable in `dashboard.html` and `devices.html`:
```javascript
const API_BASE = 'http://127.0.0.1:8000';  // Change this
```

### Add Real Device Data
Replace mock data in `devices.html` with API calls:
```javascript
async function loadDevices() {
    const token = localStorage.getItem('access_token');
    const res = await fetch(API_BASE + '/devices', {
        headers: { 'Authorization': 'Bearer ' + token }
    });
    const devices = await res.json();
    // Render devices...
}
```

### Styling Theme
Colors defined in `:root` of `styles.css`:
```css
--accent: #60e0c4      /* Teal */
--accent-2: #60a5fa    /* Blue */
--bg: #071127          /* Dark blue */
```

## Responsive Design
- Desktop: Full layout with sidebar and main content
- Tablet (980px): Stack grids, collapse pricing
- Mobile (720px): Hamburger nav, sidebar toggle, single-column grids

## Testing Credentials
Create a test account via signup, or use:
- Email: `test@example.com`
- Password: `Test@1234!` (must match your validation rules)

## Troubleshooting

### "Network error. Make sure backend is running..."
- Check backend is running on `http://127.0.0.1:8000`
- Verify no port conflicts
- Check browser console for CORS errors

### Token not persisting
- Check `localStorage` in DevTools → Application tab
- Ensure login response includes `access_token` field
- Verify token is not expired

### Shipment form not submitting
- Open DevTools → Network tab to see request/response
- Check form validation (all fields required)
- Verify backend `/shipments` endpoint accepts the POST

## Next Steps
- Wire device list to backend API
- Add shipment detail page with location map
- Implement real-time updates with WebSockets
- Add export to CSV functionality
- Integrate actual location tracking
