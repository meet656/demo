<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" />
</p>

# ⚡ ServiceHub — Local Service Finder (Ahmedabad)

> A full-stack web application that connects users with trusted local service providers — electricians, plumbers, and tutors — across Ahmedabad. Built for real-world usability and earning potential through premium listings.

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [How to Run](#-how-to-run)
- [API Endpoints](#-api-endpoints)
- [Screenshots](#-screenshots)
- [Database Schema](#-database-schema)
- [Future Improvements](#-future-improvements)
- [Deployment](#-deployment)
- [Author](#-author)

---

## 📖 About the Project

Finding a reliable electrician or plumber in Ahmedabad can be frustrating — scrolling through outdated listings, calling wrong numbers, or not knowing who to trust. **ServiceHub** solves this by providing a clean, modern platform where users can:

- Browse verified service providers by category and area
- Call or WhatsApp providers with one tap
- Rate providers to help others choose
- Save favorites for quick access later

For **service providers**, it offers visibility and premium placement to attract more customers. The admin panel makes it easy to manage all listings.

---

## ✨ Features

### 👤 User Side
| Feature | Description |
|---------|-------------|
| 🔍 **Smart Search** | Search providers by name, location, or area with live results |
| 📂 **Category Filters** | Filter by Electrician, Plumber, or Tutor with one click |
| 📍 **Area Filter** | Dropdown with 15+ Ahmedabad areas (Navrangpura, Satellite, Bopal, etc.) |
| 📇 **Provider Cards** | Each card shows name, phone, location, category, and star rating |
| 📞 **Click-to-Call** | Instant calling via `tel:` links |
| 💬 **WhatsApp Button** | Direct message via `wa.me/91XXXXXXXXXX` links |
| ⭐ **Rating System** | Rate providers 1–5 stars; averages update in real time |
| ❤️ **Favorites** | Save providers to favorites using localStorage |
| 🏆 **Premium Badges** | Premium providers are highlighted and displayed on top |
| 📱 **Responsive Design** | Works beautifully on mobile, tablet, and desktop |

### 🔐 Admin Side
| Feature | Description |
|---------|-------------|
| 🔑 **Secure Login** | Token-based authentication for admin access |
| ➕ **Add Providers** | Form to add new service providers with all details |
| ✏️ **Edit Providers** | Update any provider's information in place |
| 🗑️ **Delete Providers** | Remove providers with confirmation dialog |
| 🏅 **Premium Toggle** | Mark/unmark providers as premium (shown on top with gold badge) |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python (Flask) | REST API, routing, authentication |
| **Database** | SQLite | Lightweight data storage (zero config) |
| **Frontend** | HTML5, CSS3, Vanilla JS | UI, interactivity, dynamic rendering |
| **Styling** | Custom CSS | Dark theme, glassmorphism, animations |
| **API** | RESTful JSON | Frontend-backend communication |

---

## 📁 Project Structure

```
erning_project/
│
├── backend/
│   ├── app.py                 # Flask server — API + serves frontend
│   ├── database.db            # SQLite database (auto-created on first run)
│   └── requirements.txt       # Python dependencies
│
├── frontend/
│   ├── index.html             # User-facing homepage
│   ├── style.css              # Premium dark theme with glassmorphism
│   ├── script.js              # Search, filter, rating & favorites logic
│   └── admin.html             # Admin panel — login + CRUD dashboard
│
└── README.md                  # Project documentation (this file)
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+** installed — [Download Python](https://www.python.org/downloads/)
- **pip** (comes with Python)
- A modern web browser (Chrome, Firefox, Edge)

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/local-service-finder.git
cd local-service-finder

# 2. Navigate to the backend directory
cd backend

# 3. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 4. Install dependencies
pip install -r requirements.txt
```

> **Note:** `sqlite3` is built into Python — no extra installation needed.

---

## ▶️ How to Run

```bash
# Make sure you are in the backend/ directory
cd backend

# Start the Flask server
python app.py
```

You will see:

```
[*] Initializing Local Service Finder API...
[OK] Database initialized with sample data
[>>] Server starting at http://localhost:5000
[KEY] Admin credentials: admin / admin123
```

Now open your browser:

| Page | URL |
|------|-----|
| 🏠 **Homepage** | [http://localhost:5000](http://localhost:5000) |
| 🔐 **Admin Panel** | [http://localhost:5000/admin.html](http://localhost:5000/admin.html) |

> **Default Admin Login:** Username: `admin` · Password: `admin123`

---

## 📡 API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/services` | Get all providers (supports `?search=`, `?area=`, `?category=` query params) |
| `GET` | `/api/services/<category>` | Get providers by category (Electrician / Plumber / Tutor) |
| `GET` | `/api/services/detail/<id>` | Get a single provider by ID |
| `GET` | `/api/areas` | Get list of all available Ahmedabad areas |
| `POST` | `/api/rate-service/<id>` | Submit a rating (1–5) for a provider |

### Admin Endpoints (require authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/admin/login` | Login and receive auth token |
| `POST` | `/api/admin/logout` | Invalidate session token |
| `POST` | `/api/add-service` | Add a new service provider |
| `PUT` | `/api/update-service/<id>` | Update an existing provider |
| `DELETE` | `/api/delete-service/<id>` | Delete a provider |

**Example — Search for electricians in Satellite:**
```
GET /api/services?category=Electrician&area=Satellite
```

---

## 📸 Screenshots

### Homepage
![Homepage](screenshots/homepage.png)

### Category Filter (Electricians)
![Electricians Filter](screenshots/electricians.png)

### Admin Login
![Admin Login](screenshots/admin-login.png)

### Admin Dashboard
![Admin Dashboard](screenshots/admin-dashboard.png)

> 💡 *Add your own screenshots to a `screenshots/` folder to make these render on GitHub.*

---

## 🗄️ Database Schema

### `services` table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Auto-increment primary key |
| `name` | TEXT | Provider's business name |
| `phone` | TEXT | 10-digit phone number |
| `location` | TEXT | Detailed address / landmark |
| `area` | TEXT | Ahmedabad area (e.g., Navrangpura) |
| `category` | TEXT | Electrician / Plumber / Tutor |
| `is_premium` | INTEGER | 1 = premium (shown on top), 0 = regular |
| `rating` | REAL | Average star rating (1.0–5.0) |
| `rating_count` | INTEGER | Total number of ratings received |
| `created_at` | TIMESTAMP | Auto-set on creation |

### `ratings` table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Auto-increment primary key |
| `service_id` | INTEGER (FK) | References `services.id` |
| `rating` | INTEGER | Individual rating (1–5) |
| `created_at` | TIMESTAMP | Auto-set on creation |

---

## 🔮 Future Improvements

- [ ] **User Registration** — Let users create accounts and track their ratings
- [ ] **Image Uploads** — Allow providers to upload profile photos and work samples
- [ ] **Review Comments** — Add text reviews alongside star ratings
- [ ] **Google Maps Integration** — Show providers on a map with location pins
- [ ] **Payment Gateway** — Online payments for premium listing subscriptions
- [ ] **Email / SMS Notifications** — Alerts for new bookings and reviews
- [ ] **Multi-city Support** — Expand beyond Ahmedabad to other Gujarat cities
- [ ] **PWA Support** — Make the app installable on mobile devices
- [ ] **Advanced Analytics** — Dashboard showing call counts, views, and conversion rates

---

## 🌐 Deployment

### Deploy on Render (Free Tier)

1. Push your project to a GitHub repository
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. Connect your GitHub repo and configure:
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && python app.py`
4. Update `app.run()` in `app.py` for production:
   ```python
   app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
   ```

### Deploy on PythonAnywhere (Free Tier)

1. Upload your project files
2. Set up a Flask web app pointing to `backend/app.py`
3. Install dependencies via the console: `pip install -r requirements.txt`

---

## 👨‍💻 Author

**Meet**

- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/your-profile)

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ in Ahmedabad &nbsp;|&nbsp; ⭐ Star this repo if you found it useful!
</p>
