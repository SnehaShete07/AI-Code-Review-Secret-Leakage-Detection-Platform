# 🐾 PAMS — Pet Adoption Management System

A full-stack web application for managing pet adoptions, built with **Python (Flask)**, **SQLite**, and **Bootstrap 5**. This project demonstrates end-to-end database-driven application development, including relational schema design, CRUD operations, server-side validation, session-based authentication, and data export.

---

## 🚀 Live Demo

> Clone and run locally in under 2 minutes — see [Quick Start](#-quick-start).

---

## ✨ Features

### Public (User-Facing)
| Feature | Details |
|---|---|
| 🐾 **Browse Pets** | View all available pets with live search, species filter, and gender filter |
| 🔍 **Search** | Full-text search across pet name, breed, and description |
| 📋 **Adoption Form** | Multi-field form with server-side input validation (email regex, phone format, required fields) |
| 🔄 **Duplicate Prevention** | Prevents the same user from submitting duplicate requests for the same pet |
| 🏠 **Home Dashboard** | Live stats (total, available, adopted, pending) and recently added pets |

### Admin Panel (Authenticated)
| Feature | Details |
|---|---|
| 🔐 **Secure Login** | SHA-256 hashed passwords, session-based authentication, protected routes via decorator |
| 📊 **Dashboard** | Aggregated KPIs and recent adoption request table |
| ➕ **Add/Edit/Delete Pets** | Full CRUD with species dropdown, age validation, image URL support |
| ✅ **Approve / Reject Requests** | One-click status management; pet status synced automatically |
| 📥 **CSV Export** | Export all pets or all adoption requests as downloadable `.csv` files |

### Technical Highlights
- **Relational schema** with 4 normalized tables and enforced foreign keys (`PRAGMA foreign_keys = ON`)
- **Database indexes** on `status`, `species`, and foreign key columns for query performance
- **WAL journal mode** for improved concurrent read performance
- **Parameterized SQL** throughout — no raw string interpolation (SQL injection safe)
- **`g`-scoped DB connections** per Flask request with teardown cleanup
- **Custom error pages** for 404 and 500
- **Decorator-based auth guard** (`@admin_required`) for all admin routes

---

## 🧱 Architecture

```
PAMS/
├── app.py              # Flask routes, business logic, request handling
├── database.py         # Schema init, indexes, seed data, connection helper
├── requirements.txt    # Python dependencies
├── petadoption.db      # SQLite database (auto-created on first run)
├── static/
│   └── style.css       # Custom CSS (Playfair Display + DM Sans, CSS variables)
└── templates/
    ├── base.html            # Shared layout, navbar, flash messages, footer
    ├── home.html            # Landing page with stats + recent pets
    ├── pets.html            # Browse page with search & filter
    ├── adopt.html           # Adoption request form
    ├── admin_login.html     # Admin authentication
    ├── admin_dashboard.html # Admin KPI overview
    ├── admin_pets.html      # Pet management table
    ├── add_pet.html         # Add pet form
    ├── edit_pet.html        # Edit pet form
    ├── admin_requests.html  # Adoption request management
    ├── 404.html             # Custom 404 page
    └── 500.html             # Custom 500 page
```

### 3-Tier Architecture
```
┌──────────────────┐     HTTP      ┌──────────────────┐     SQL       ┌──────────────────┐
│  Presentation    │ ◄──────────► │  Application     │ ◄──────────► │  Data Layer      │
│  (HTML/CSS/JS)   │               │  (Flask/Python)  │               │  (SQLite)        │
│  Bootstrap 5     │               │  app.py          │               │  4 Tables        │
│  Jinja2 Templates│               │  database.py     │               │  FK Constraints  │
└──────────────────┘               └──────────────────┘               └──────────────────┘
```

---

## 🗄️ Database Schema (ERD Summary)

```
Users               Pets                  Adoption_Requests
─────────────       ─────────────────     ────────────────────────
user_id   PK        pet_id      PK        request_id  PK
name                name                  user_id     FK → Users
email     UNIQUE    species               pet_id      FK → Pets
phone               breed                 request_date
address             age                   status  (Pending/Approved/Rejected)
created_at          gender                notes
                    description           UNIQUE(user_id, pet_id)
                    image_url
                    status  (Available/Pending/Adopted)
                    added_on
```

**Normalization:** Schema is in **3NF** — no transitive dependencies; each non-key attribute depends only on the primary key. Adoption data is separated from user and pet data to avoid update anomalies.

---

## ⚙️ Quick Start

### Prerequisites
- Python 3.9+
- pip

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/Mini-Project-DBMS.git
cd Mini-Project-DBMS

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app (database is auto-initialized on first run)
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

### Default Admin Credentials
| Field | Value |
|---|---|
| URL | `/admin/login` |
| Username | `admin` |
| Password | `admin123` |

> ⚠️ Change these before any public deployment.

---

## 🔒 Security Practices Implemented

- **Password hashing** — SHA-256 (upgrade to `bcrypt` for production)
- **Parameterized queries** — all SQL uses `?` placeholders, not f-strings
- **CSRF awareness** — secret key set for session integrity
- **Input validation** — server-side regex checks on email and phone
- **Auth decorator** — all admin routes protected via `@admin_required`
- **FK enforcement** — `PRAGMA foreign_keys = ON` prevents orphan records

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3 |
| Database | SQLite 3 (via `sqlite3` stdlib) |
| Frontend | HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons |
| Templating | Jinja2 |
| Data Export | Python `csv` module (stdlib) |
| Fonts | Google Fonts (Playfair Display, DM Sans) |

---

## 📈 Possible Extensions

- [ ] Flask-Login for proper session management
- [ ] bcrypt for password hashing
- [ ] Image upload (store to `/static/uploads/`, save path in DB)
- [ ] Email notification on request approval (Flask-Mail)
- [ ] Pagination on pet listings
- [ ] Admin analytics chart (Chart.js + aggregation queries)
- [ ] Migrate to PostgreSQL with SQLAlchemy ORM for production scale
- [ ] Deploy to Render or Railway (free tier)

---

## 👩‍💻 Author

Built as a DBMS mini-project demonstrating relational database design, full-stack web development, and software engineering best practices.

---

## 📄 License

MIT License — free to use, modify, and distribute.
