# Arabic Institute Enterprise API

A production-grade Django REST Framework API serving as the middleware layer for the Arabic Institute Enterprise Learning & Certification Platform. This repository forms the backend of a three-layer enterprise architecture.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Security](#security)
- [API Endpoints](#api-endpoints)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Technical Decisions](#technical-decisions)
- [AI Usage](#ai-usage)

---

## Architecture Overview

This application follows a strict three-layer enterprise architecture:
```
┌─────────────────────────────────────┐
│           React Frontend            │
│   (arabic-institute-frontend repo)  │
└──────────────┬──────────────────────┘
               │ HTTP/REST (JWT)
               ▼
┌─────────────────────────────────────┐
│        Django REST Framework        │  ← THIS REPO
│   Authentication · Business Logic   │
│   Validation · Authorisation        │
└──────────────┬──────────────────────┘
               │ Django ORM only
               ▼
┌─────────────────────────────────────┐
│          PostgreSQL Database        │
│      (never accessed directly       │
│        by the frontend)             │
└─────────────────────────────────────┘
```

**Key principle:** The frontend never touches the database. All business logic, validation, and data access lives exclusively in this middleware layer.

---

## Technology Stack

| Component | Technology |
|---|---|
| Framework | Django 5.x + Django REST Framework |
| Authentication | JWT via djangorestframework-simplejwt |
| Database | PostgreSQL via psycopg2 |
| Media Storage | Cloudinary |
| Email | SendGrid |
| PDF Generation | ReportLab |
| Testing | Django TestCase + DRF APIClient |
| Coverage | coverage.py (90%+) |
| Deployment | Render |
| CI/CD | GitHub Actions |

---

## Features

### Authentication & User Management
- JWT-based login and registration
- Role-based access control (Student / Teacher / Admin)
- Editable user profiles with Cloudinary avatar storage
- Password reset via SendGrid email with secure token
- Token blacklisting on logout

### Course Management
- Full course lifecycle: Draft → Published → Archived
- Admin-only course creation and management
- Prerequisite course relationships (many-to-many)
- Configurable pass marks per course

### Cohort Management
- Cohorts link courses to teachers with capacity limits
- Enrolment open/closed control
- Real-time capacity tracking

### Enrolment Engine (Core Domain Feature)
The enrolment system enforces the following business rules server-side:

| Rule | Description |
|---|---|
| Capacity | Cannot enrol if cohort is full |
| Enrolment window | Cannot enrol if enrolment is closed |
| Course status | Cannot enrol in unpublished course |
| Prerequisites | Must complete prerequisite courses first |
| Duplicate prevention | Cannot enrol twice in same cohort |

Status lifecycle: `pending → active → completed / failed / withdrawn`

Status is automatically updated when a teacher records grade and attendance:
- Attendance ≥ 75% AND grade ≥ pass mark → `completed`
- Otherwise → `failed`

### Certification Engine
A certificate can only be issued when ALL five criteria are met:
1. Enrolment status is `completed`
2. Attendance ≥ 75%
3. Final grade ≥ course pass mark
4. Fees marked as paid
5. Teacher approval given

Certificates are immutable after issuance. A PDF is automatically generated using ReportLab and stored on Cloudinary.

---

## Security

| Feature | Implementation |
|---|---|
| Password hashing | Django PBKDF2 (default) |
| Authentication | JWT access tokens (60 min) + refresh tokens (7 days) |
| Token blacklisting | Blacklisted on logout via SimpleJWT blacklist app |
| Role enforcement | Custom DRF permission classes per endpoint |
| Input sanitization | bleach HTML stripping + regex username validation |
| Security headers | X-Frame-Options: DENY · X-Content-Type-Options: nosniff |
| Secret management | All secrets via environment variables, never in code |
| CORS | Restricted to known frontend origins |
| HTTPS | Enforced in production via Render |

---

## API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | None | Register new user |
| POST | `/api/auth/login/` | None | Login, returns JWT tokens |
| POST | `/api/auth/logout/` | JWT | Blacklist refresh token |
| POST | `/api/auth/token/refresh/` | None | Refresh access token |
| GET/PATCH | `/api/auth/profile/` | JWT | Get or update own profile |
| POST | `/api/auth/password-reset/` | None | Request password reset email |
| POST | `/api/auth/password-reset/confirm/` | None | Confirm password reset |

### Courses
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/courses/` | JWT | List courses (published only for students) |
| POST | `/api/courses/` | Admin | Create course |
| GET/PATCH/DELETE | `/api/courses/<id>/` | JWT/Admin | Course detail |
| GET | `/api/courses/cohorts/` | JWT | List cohorts |
| POST | `/api/courses/cohorts/` | Admin | Create cohort |
| GET/PATCH | `/api/courses/cohorts/<id>/` | JWT/Admin+Teacher | Cohort detail |

### Enrolments
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/enrolments/` | Student | Enrol in cohort |
| GET | `/api/enrolments/my/` | Student | Own enrolments |
| GET | `/api/enrolments/cohort/<id>/` | Admin/Teacher | Cohort roster |
| PATCH | `/api/enrolments/<id>/` | Admin/Teacher | Update grade/attendance |
| PATCH | `/api/enrolments/<id>/withdraw/` | Student | Withdraw from cohort |

### Certificates
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/certificates/` | Admin/Teacher | Issue certificate |
| GET | `/api/certificates/my/` | Student | Own certificates |
| GET | `/api/certificates/all/` | Admin/Teacher | All certificates |

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Git

### Local Development
```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/arabic-institute-api.git
cd arabic-institute-api

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your values (see Environment Variables below)

# Create the database
psql -U postgres -c "CREATE DATABASE arabic_institute;"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000`

---

## Environment Variables

Create a `.env` file in the root directory. Never commit this file.
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DB_NAME=arabic_institute
DB_USER=your-postgres-username
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432

# Frontend URL (for password reset links)
FRONTEND_URL=http://localhost:5173

# SendGrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxx
DEFAULT_FROM_EMAIL=your-verified-email@example.com

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

A `.env.example` file is included in the repository with all required keys and no values.

---

## Running Tests
```bash
# Run all tests
python manage.py test

# Run with coverage report
coverage run --source='.' manage.py test
coverage report

# Generate HTML coverage report
coverage html
open htmlcov/index.html
```

### Test Structure

Tests are organised by app and type:
```
users/tests/
├── test_models.py        # Unit tests — User model properties
├── test_serializers.py   # Unit tests — Serializer validation
├── test_views.py         # Integration tests — Auth API endpoints
└── test_security.py      # Security tests — Rate limiting, blacklisting, sanitization

courses/tests/
├── test_models.py        # Unit tests — Course and Cohort model logic
└── test_views.py         # Integration tests — Course API endpoints

enrolments/tests/
├── test_models.py        # Unit tests — Enrolment validation (clean method)
├── test_services.py      # Unit tests — update_status(), can_issue_certificate
└── test_views.py         # Integration tests — Enrolment API endpoints

certificates/tests/
├── test_models.py        # Unit tests — Certificate eligibility
└── test_views.py         # Integration tests — Certificate API endpoints
```

**Coverage: 90%+**

### What is tested and why

| Test Type | Purpose | Example |
|---|---|---|
| Unit — models | Verify business logic in isolation | `can_issue_certificate` returns False when fees unpaid |
| Unit — serializers | Verify validation rules | Password mismatch raises validation error |
| Unit — services | Verify status transitions | Grade 70 + attendance 80 → status completed |
| Integration — API | Verify HTTP behaviour end to end | POST /enrolments/ returns 400 when cohort full |
| Security | Verify protection mechanisms | 6th login attempt returns 429 |
| Permission | Verify role boundaries | Student cannot create course (403) |

---

## Deployment

### Live URL
**https://arabic-institute-api.onrender.com**

### Render Deployment

The application is deployed on Render's free tier with:
- Managed PostgreSQL database
- Environment variables configured securely (never in code)
- Auto-deploy on push to `main` branch
- HTTPS enforced

### CI/CD Pipeline

GitHub Actions runs on every push and pull request to `main`:
```yaml
# .github/workflows/ci.yml
# Spins up PostgreSQL, installs dependencies, runs all tests
# Prevents broken code from being merged to main
```

View the CI badge at the top of this README for current build status.

---

## Technical Decisions

### Why Django REST Framework?
DRF provides a mature, well-tested foundation for building REST APIs with built-in support for serialization, authentication, permissions, and browsable API documentation. It aligns directly with the module's supported stack.

### Why JWT Authentication?
JWT tokens are stateless, scalable, and widely used in enterprise applications. They allow the frontend to authenticate without session state on the server, which is important for horizontal scaling.

### Why separate Django apps?
Each domain concern (`users`, `courses`, `enrolments`, `certificates`) is its own Django app. This follows the single responsibility principle and makes the codebase easier to maintain, test, and extend independently.

### Why ReportLab for PDFs?
ReportLab is a pure Python PDF library with no external dependencies or browser requirements. It generates PDFs in memory, which are then streamed directly to Cloudinary - no disk I/O required.

### Why bleach for sanitization?
bleach is a well-maintained Python library specifically designed for sanitizing HTML input. Combined with regex validation on usernames, it prevents XSS attacks without over-engineering the solution.

---

## AI Usage

This project was developed with the assistance of Claude (Anthropic) as a coding guide and pair programming tool. Claude was used to:
- Suggest architectural patterns and enterprise best practices
- Generate boilerplate code which was then reviewed and modified
- Debug errors and explain solutions
- Suggest test cases

All code has been reviewed and understood, and i AM responsible for all implementation decisions and can explain any part of the codebase.

---

## Repository Structure
```
arabic-institute-api/
├── config/               # Django project settings and URL config
│   ├── settings.py       # All configuration, env-var driven
│   ├── urls.py           # Root URL routing
│   └── permissions.py    # Custom DRF permission classes
├── users/                # Authentication and user management
├── courses/              # Course and cohort management
├── enrolments/           # Enrolment engine with business logic
├── certificates/         # Certificate issuance workflow
├── .github/workflows/    # GitHub Actions CI pipeline
├── requirements.txt      # Python dependencies
├── Procfile              # Render deployment config
├── build.sh              # Render build script
└── manage.py
```