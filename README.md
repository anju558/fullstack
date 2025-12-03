<<<<<<< HEAD
# Full Stack Supply Chain Management System

A complete full-stack application for real-time supply chain management with Docker orchestration, Kafka streaming, MongoDB persistence, and FastAPI backend.

## 🎯 Project Overview

This project demonstrates a modern full-stack application architecture with:
- **Real-time data streaming** via Kafka
- **Containerized microservices** using Docker
- **REST API** with JWT authentication  
- **MongoDB** for persistent storage
- **WebSocket-ready** architecture for live updates
- **User authentication** with secure password handling
- **Responsive web interface** with HTML/CSS/JavaScript

## ✨ Features

### User Management
- User signup with email validation
- Password strength validation (8+ chars, uppercase, lowercase, numbers, special chars)
- JWT-based authentication
- Secure session management with HTTP-only cookies
- User profile page with account details

### Shipment Management
- Create and track shipments
- View personal shipment history
- Shipment details with location and container info
- CAPTCHA protection for shipment creation

### Real-Time Device Tracking
- Socket server generates test device data
- Kafka producer reads from socket
- Kafka consumer stores to MongoDB
- Live device data visualization
- Battery level and temperature monitoring
- Location tracking

### API Endpoints
- Complete REST API with JSON responses
- Swagger documentation at `/docs`
- Authentication required for protected endpoints
- CORS enabled for cross-origin requests

## 🏗️ Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
┌──────▼──────────────────────────────┐
│   FastAPI Backend (Port 8000)       │
│  - Authentication & Authorization   │
│  - REST API endpoints               │
│  - HTML/Template rendering          │
└──────┬──────────────────────────────┘
       │
   ┌───┴────┬───────────┐
   │         │           │
   │         │           │
┌──▼──┐  ┌──▼──┐   ┌────▼───┐
│ MongoDB  │ Kafka │  Socket  │
│          │       │ (Test)   │
└──────────┴───────┴──────────┘
       ▲
       │
    ┌──┴──────┐
    │Consumer  │
    │(Kafka)   │
    └──┬───────┘
       │
    ┌──▼───────┐
    │ Producer  │
    │ (Kafka)   │
    └───────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Windows PowerShell or Command Prompt
- ~2GB free disk space

### Installation & Running

```powershell
# 1. Navigate to project
cd c:\Users\anjal\OneDrive\Desktop\fullstack\fullstack

# 2. Start application (Option A - Automatic)
.\start.ps1

# 2. Start application (Option B - Manual)
docker-compose up --build

# 3. Wait 60-90 seconds for all services to start
# 4. Access at http://localhost:8000
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **SETUP_GUIDE.md** | Complete setup and architecture documentation |
| **IMPLEMENTATION_SUMMARY.md** | Detailed list of what was implemented |
| **QUICK_REFERENCE.md** | Quick commands and troubleshooting |
| **FILE_MODIFICATIONS.md** | Complete list of all file changes |

## 🌐 Access Points

Once running:

| Service | URL | Purpose |
|---------|-----|---------|
| Web App | http://localhost:8000 | Main application |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |
| MongoDB | localhost:27017 | Database (admin/password) |
| Kafka | localhost:9092 | Message broker |
| Socket Server | localhost:5050 | Test data source |

## 🔐 Default Credentials

```
MongoDB Username: admin
MongoDB Password: password
Database Name: scmlitedb

JWT Secret: mysecretkey123mysecretkey123mysecretkey123
Token Expiration: 24 hours
```

## 📋 API Endpoints

### Authentication
- `POST /signup` - Register new user
- `POST /login` - Login user
- `GET /logout` - Logout user

### User
- `GET /profile` - View profile page
- `GET /api/profile` - Get profile data (JSON)

### Shipments
- `GET /dashboard` - Dashboard view
- `GET /my-shipments` - List user's shipments
- `GET /api/my-shipments` - Shipments (JSON)
- `GET /create-shipment` - Create shipment form
- `POST /create-shipment` - Submit shipment
- `POST /shipments` - JSON API for shipments

### Device Data
- `GET /devices` - View device data
- `GET /api/devices` - Device data (JSON)
- `GET /device-stream/{device_id}` - Device details
- `GET /view-stream` - Stream view page

## 🐳 Docker Services

### MongoDB
- Image: `mongo:latest`
- Port: 27017
- Admin: admin/password
- Database: scmlitedb
- Features: Health checks, persistent volume

### Zookeeper
- Image: `confluentinc/cp-zookeeper:7.4.0`
- Port: 2181
- Purpose: Kafka coordination

### Kafka
- Image: `confluentinc/cp-kafka:7.4.0`
- Port: 9092
- Topic: shipment_data
- Auto-create topics enabled

### Socket Server
- Image: Custom (Python 3.10)
- Port: 5050
- Purpose: Generates test device data
- Sends: Battery level, temperature, location

### Kafka Producer
- Image: Custom (Python 3.10)
- Purpose: Reads from socket → sends to Kafka
- Connection: Socket Server → Kafka

### Kafka Consumer
- Image: Custom (Python 3.10)
- Purpose: Reads from Kafka → stores in MongoDB
- Connection: Kafka → MongoDB

### FastAPI Backend
- Image: Custom (Python 3.10)
- Port: 8000
- Framework: FastAPI
- Features: REST API, JWT auth, templates

## 🧪 Testing the Application

### 1. Test User Signup
```
1. Visit http://localhost:8000
2. Click "Sign Up"
3. Enter username (4+ chars)
4. Enter email
5. Enter password (must meet all requirements)
6. Confirm password
7. Click "Sign Up"
```

### 2. Test Profile Page
```
1. Login with your account
2. Click "👤 My Profile" in sidebar
3. View your information
4. Profile loaded from /api/profile endpoint
```

### 3. Test Shipment Creation
```
1. Click "➕ New Shipment"
2. Fill in shipment details
3. Solve CAPTCHA
4. Submit
5. View in "My Shipments"
```

### 4. Test Device Streaming
```
1. Click "🚪 Device Data"
2. View real-time device data
3. Data flows: Socket → Producer → Kafka → Consumer → MongoDB
```

## 🔧 Troubleshooting

### Services not starting?
```powershell
# Check Docker
docker version

# Check specific service logs
docker-compose logs kafka
docker-compose logs mongodb
docker-compose logs backend

# Wait longer (can take 90 seconds)
# Services start in order: Zookeeper → MongoDB → Kafka → Others
```

### MongoDB connection failed?
```powershell
# Check MongoDB
docker-compose logs mongodb

# Test connection
docker exec mongodb mongosh -u admin -p password --authenticationDatabase admin
```

### Kafka not working?
```powershell
# Check Kafka logs
docker-compose logs kafka

# List topics
docker exec kafka kafka-topics --list --bootstrap-server kafka:9092
```

### Reset everything
```powershell
# Stop all services
docker-compose down

# Remove data
docker-compose down -v

# Restart fresh
docker-compose up --build
```

## 📁 Project Structure

```
fullstack/
├── backend/                    # FastAPI application
│   ├── main.py                # Main app with all endpoints
│   ├── database.py            # MongoDB configuration
│   ├── auth.py                # JWT authentication
│   ├── models.py              # Pydantic models
│   ├── templates/
│   │   ├── profile.html       # User profile page
│   │   ├── dashboard.html     # Dashboard
│   │   ├── my_shipments.html  # Shipment list
│   │   └── ...                # Other templates
│   ├── static/
│   │   ├── styles.css         # Styling (app is server-rendered; no custom client JS)
│   ├── Dockerfile
│   └── requirements.txt
│
├── producer/                  # Kafka Producer
│   ├── producer.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── consumer/                  # Kafka Consumer
│   ├── consumer.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── socket_server/             # Test data generator
│   ├── srever.py
│   └── Dockerfile
│
├── docker-compose.yml         # All services
├── .env                       # Configuration
├── SETUP_GUIDE.md            # Setup instructions
├── IMPLEMENTATION_SUMMARY.md # What was done
├── QUICK_REFERENCE.md        # Quick commands
├── FILE_MODIFICATIONS.md     # Change log
├── start.ps1                 # Quick start
├── verify.ps1                # Verification
└── README.md                 # This file
```

## 🔍 Key Components

### FastAPI Backend
- RESTful API with proper error handling
- JWT authentication with access tokens
- MongoDB integration via PyMongo
- Jinja2 templates for HTML rendering
- CORS enabled for all origins
- OAuth2 password bearer scheme

### Database (MongoDB)
- Collections: users, shipments, shipment_data
- Indexes for common queries
- TTL indexes for session management
- Replica set ready

### Message Queue (Kafka)
- Topic: shipment_data
- Replication factor: 1
- Auto-create topics enabled
- Partition management

### Data Pipeline
- Socket Server → Data generator
- Kafka Producer → Message publisher
- Kafka Broker → Distribution
- Kafka Consumer → Persistent storage
- FastAPI → Data visualization

## 📊 Data Models

### User
```json
{
  "_id": "ObjectId",
  "username": "string",
  "email": "string",
  "password_hash": "string",
  "created_at": "datetime"
}
```

### Shipment
```json
{
  "_id": "ObjectId",
  "Shipment_Number": "string",
  "Route_Details": "string",
  "Device": "string",
  "created_by_email": "string",
  "created_at": "datetime",
  ...
}
```

### Device Data
```json
{
  "_id": "ObjectId",
  "Battery_Level": "float",
  "Device_ID": "int",
  "First_Sensor_temperature": "float",
  "Route_From": "string",
  "Route_To": "string"
}
```

## 🔒 Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token-based authentication
- ✅ HTTP-only secure cookies
- ✅ CORS configuration
- ✅ SQL injection prevention
- ✅ XSS protection via HTML escaping
- ✅ CAPTCHA for public forms
- ✅ Input validation
- ✅ Error message sanitization

## 📈 Performance

- Connection pooling for MongoDB
- Kafka message batching
- Database indexing
- Efficient API queries
- Caching-ready architecture
- Stateless API design

## 🎓 Learning Outcomes

This project demonstrates:
- Docker and containerization
- Microservices architecture
- Message queue implementation
- REST API design
- Authentication & authorization
- Real-time data streaming
- Database design and optimization
- Frontend-backend integration

## 🚀 Deployment Considerations

For production deployment:
1. Change all default credentials
2. Use strong JWT secret key
3. Configure HTTPS/TLS
4. Set up proper logging
5. Implement rate limiting
6. Configure CORS for specific domains
7. Use environment-specific configs
8. Set up monitoring and alerts
9. Implement backup strategies
10. Use managed database services

## 📞 Support

For detailed information:
1. Read **SETUP_GUIDE.md** for complete setup
2. Check **QUICK_REFERENCE.md** for quick commands
3. Review **IMPLEMENTATION_SUMMARY.md** for features
4. See **FILE_MODIFICATIONS.md** for changes made

## ✅ Verification

Before starting, run:
```powershell
.\verify.ps1
```

This checks:
- All files are present
- Configuration is correct
- Dockerfiles are valid
- Requirements are specified

## 🎉 Ready to Go!

Everything is configured and ready. Start with:

```powershell
docker-compose up --build
```

Then visit: **http://localhost:8000**

---

**Status**: ✅ Complete and ready for deployment

**Last Updated**: November 15, 2025

**Version**: 1.0.0
=======
# fullstack
website
hi this is anjali
i am doing fullstack project
>>>>>>> c0dec9c98cd39b4d5a749bd0a276da4e2180991a
