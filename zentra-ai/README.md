# ⚡ Zentra AI — AI-Powered Subscription Management Platform

> Automatically detect, track, analyze, and optimize your digital subscriptions using AI.

---

## 🌟 Overview

Zentra AI is a full-stack SaaS platform that acts as your personal subscription intelligence assistant. It helps you:

- 🤖 **Auto-detect subscriptions** from Gmail emails, bank transactions, and SMS
- 📊 **Track & visualize** all subscriptions in one centralized dashboard
- 💡 **Get AI recommendations** to cancel unused, downgrade expensive, or switch services
- ⏰ **Receive proactive alerts** via email, SMS, WhatsApp, and push notifications
- 💰 **Save money** by identifying duplicate, unused, and cost-inefficient subscriptions

---

## 🏗️ Architecture

```
zentra-ai/
├── backend/                  # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── config.py         # App configuration
│   │   ├── database.py       # SQLAlchemy DB setup
│   │   ├── models/           # Database models
│   │   │   ├── user.py       # User model
│   │   │   ├── subscription.py  # Subscription + Usage models
│   │   │   ├── notification.py  # Notification models
│   │   │   └── analytics.py  # Spending snapshots
│   │   ├── api/              # REST API routers
│   │   │   ├── auth.py       # Authentication (JWT)
│   │   │   ├── subscriptions.py  # Subscription CRUD + scanning
│   │   │   ├── analytics.py  # Analytics & insights
│   │   │   └── notifications.py  # Notification management
│   │   ├── services/         # Business logic services
│   │   │   ├── auth.py       # JWT auth helpers
│   │   │   ├── gmail_scanner.py  # Gmail API integration
│   │   │   ├── bank_scanner.py   # Plaid bank integration
│   │   │   └── notification_service.py  # Multi-channel notifications
│   │   └── ai/               # AI/ML modules
│   │       ├── subscription_detector.py   # Detect subscriptions from text
│   │       ├── recommendation_engine.py   # Generate personalized recommendations
│   │       └── analytics_engine.py        # Spending analytics & trends
│   ├── tests/
│   │   └── test_ai.py        # 22 unit tests for AI modules
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React Frontend
│   ├── src/
│   │   ├── App.js            # Main React app with routing
│   │   ├── pages/
│   │   │   ├── Dashboard.js  # Main dashboard with charts
│   │   │   ├── Subscriptions.js  # Subscription management
│   │   │   ├── Analytics.js  # Detailed analytics
│   │   │   ├── Recommendations.js  # AI recommendations
│   │   │   ├── NotificationsPage.js  # Notification center
│   │   │   ├── Settings.js   # Profile & preferences
│   │   │   ├── Login.js      # Authentication
│   │   │   └── Register.js   # Registration
│   │   ├── components/
│   │   │   └── common/
│   │   │       ├── Layout.js  # App layout with sidebar
│   │   │       └── NotificationBell.js  # Bell with unread count
│   │   ├── hooks/
│   │   │   └── useAuthStore.js  # Zustand auth state
│   │   ├── services/
│   │   │   └── api.js        # Axios API client
│   │   └── styles/
│   │       └── globals.css   # Global CSS variables & utilities
│   ├── public/index.html
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml        # Local development stack
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docker.com) & Docker Compose
- Or: Python 3.11+, Node.js 18+, PostgreSQL 15+

### Quick Start (Docker)

```bash
# Clone and enter the zentra-ai directory
cd zentra-ai

# Start everything
docker-compose up --build

# App will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/docs
```

### Manual Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL and API keys

# Run database migrations
python -c "from app.database import Base, engine; from app import models; Base.metadata.create_all(engine)"

# Start server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
# Opens at http://localhost:3000
```

---

## 🔌 Integrations

| Integration | Purpose | Required |
|-------------|---------|---------|
| **PostgreSQL** | Primary database | Yes |
| **Gmail API** | Scan emails for subscriptions | Optional |
| **Plaid** | Bank/card transaction scanning | Optional |
| **Twilio** | SMS & WhatsApp notifications | Optional |
| **SendGrid** | Email notifications | Optional |
| **Firebase** | Push notifications | Optional |
| **Redis** | Background task queue | Optional |

Configure integrations by setting environment variables in `backend/.env`.

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login (returns JWT) |
| GET | `/api/auth/me` | Get current user |
| PUT | `/api/auth/me` | Update profile |
| GET | `/api/auth/gmail/authorize` | Start Gmail OAuth |

### Subscriptions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subscriptions` | List subscriptions |
| POST | `/api/subscriptions` | Add subscription |
| PUT | `/api/subscriptions/{id}` | Update subscription |
| DELETE | `/api/subscriptions/{id}` | Delete subscription |
| POST | `/api/subscriptions/{id}/cancel` | Cancel subscription |
| POST | `/api/subscriptions/{id}/log-usage` | Log service usage |
| POST | `/api/subscriptions/scan/gmail` | Auto-scan Gmail |
| POST | `/api/subscriptions/scan/bank` | Auto-scan bank transactions |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | All dashboard data |
| GET | `/api/analytics/summary` | Spending summary |
| GET | `/api/analytics/category-breakdown` | By category |
| GET | `/api/analytics/monthly-trend` | 6-month trend |
| GET | `/api/analytics/upcoming-renewals` | Next 30 days |
| GET | `/api/analytics/savings-potential` | Savings analysis |
| GET | `/api/analytics/recommendations` | AI recommendations |
| GET | `/api/analytics/insights` | AI insights |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | List notifications |
| PUT | `/api/notifications/{id}/read` | Mark as read |
| PUT | `/api/notifications/mark-all-read` | Mark all read |
| GET | `/api/notifications/preferences` | Get preferences |
| PUT | `/api/notifications/preferences` | Update preferences |

---

## 🤖 AI Modules

### Subscription Detector
Uses pattern recognition and NLP to identify subscriptions from:
- **Gmail emails**: Detects invoice/receipt emails with amount extraction
- **Bank transactions**: Identifies recurring merchant payments
- **SMS**: Parses payment notification messages

Supports 20+ known merchants (Netflix, Spotify, Amazon Prime, etc.) with confidence scoring.

### Recommendation Engine
Generates personalized cost-optimization recommendations:
- 🗑️ **Cancel unused** — Services not used in 30+ days
- ⏸️ **Pause subscriptions** — Low-usage services
- 🔄 **Switch to alternatives** — Cheaper equivalent services
- 📉 **Annual plan discounts** — Save 20-30% with yearly billing
- 🔁 **Duplicate detection** — Multiple services in same category

### Analytics Engine
Computes:
- Monthly/annual spending totals
- Category-wise spending breakdown
- 6-month historical trend
- Upcoming renewal calendar
- Savings opportunity analysis

---

## 🔒 Security Features

- **JWT authentication** with configurable expiry
- **Bcrypt password hashing** (passlib)
- **Per-user data isolation** — All queries filtered by user ID
- **OAuth 2.0** for Gmail integration (read-only scope)
- **Permission-based API access** for financial data
- **CORS** configured for frontend origin

---

## 🧪 Running Tests

```bash
cd backend
python -m pytest tests/test_ai.py -v

# Expected output:
# 22 passed in 0.05s
```

Tests cover:
- Subscription detection from email, bank transactions, SMS
- Recommendation generation logic
- Analytics computation accuracy
- Edge cases (unused services, duplicates, renewals)

---

## 🚀 Production Deployment

### AWS ECS / Google Cloud Run

1. Build and push Docker images to ECR/GCR
2. Set production environment variables (SECRET_KEY, database URL, API keys)
3. Use a managed PostgreSQL (RDS / Cloud SQL)
4. Use managed Redis (ElastiCache / Memorystore)
5. Configure HTTPS with a load balancer
6. Set `DEBUG=False` and `FRONTEND_URL` to your domain

### Environment Variables for Production

```bash
SECRET_KEY=<random-64-char-string>
DATABASE_URL=postgresql://user:pass@prod-host:5432/zentra_db
REDIS_URL=redis://prod-redis:6379/0
FRONTEND_URL=https://app.zentra.ai
DEBUG=False

# Required for full functionality:
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
PLAID_CLIENT_ID=...
PLAID_SECRET=...
SENDGRID_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

---

## 📱 Frontend Features

| Page | Features |
|------|---------|
| **Dashboard** | Spending overview, trend chart, category pie, upcoming renewals, top AI recommendations |
| **Subscriptions** | Grid view, status filters, category filters, Gmail/bank scanning, add modal, cancel action |
| **Analytics** | Area chart, pie chart, bar chart, category table with progress bars, savings opportunity card |
| **Recommendations** | Priority-grouped AI suggestions with potential savings, dismiss action |
| **Notifications** | In-app notification center, unread count badge, mark as read |
| **Settings** | Profile edit, integration connections, notification channel & type toggles |

---

## 🔮 Roadmap

- [ ] React Native mobile app
- [ ] Celery background jobs for scheduled reminders
- [ ] Voice synthesis alerts (Twilio Voice API)
- [ ] Telegram bot integration
- [ ] OTT platform direct API integrations
- [ ] ML model for subscription categorization
- [ ] Budget alerts and spending limits
- [ ] Family subscription sharing tracker
- [ ] Export to CSV/PDF

---

## 📄 License

MIT License — Free to use and modify.
