# CyberNews Tracker

A secure, role-based Flask web application for tracking cybersecurity news headlines. Features user authentication, an admin dashboard, contact forms, and dynamic content rendering.

---

## Features

### User Authentication & Authorization
- **User Registration** — Create new accounts with username and password validation (password confirmation required)
- **Secure Login** — Passwords hashed with Werkzeug; session-based authentication with 2-hour expiration
- **Role-Based Access Control** — Two-tier system: `user` and `admin`
- **First-User Admin** — The first registered account automatically becomes an admin
- **Session Security** — HTTPOnly cookies, configurable secure flags, and SameSite=Lax protection

### Admin Dashboard
- **User Management** — View all registered users in a sortable table
- **Role Toggling** — Promote users to admin or demote admins to user (cannot self-demote)
- **Account Deletion** — Delete any user account; self-deletion triggers automatic logout
- **Action Feedback** — Flash messages confirm every admin action

### News Headlines
- **Dynamic Greeting** — Time-based greeting message (Morning/Afternoon/Evening/Night)
- **Article Feed** — Click "Refresh Headlines" to load articles from `Articles.json`
- **Progressive Loading** — Articles append one-by-one; "all up to date" message when exhausted

### Contact Form
- **Profile Submission** — Collect name, age, gender, title, and message
- **Validation** — All fields required with HTML5 client-side validation
- **Result Display** — Submitted data rendered back in a clean summary view

### UI/UX
- **Responsive Design** — Mobile-friendly layout with collapsible header
- **Cyber-Themed Styling** — Dark headers, cyan accents, neon glow effects
- **Cookie Notice** — Auto-dismissible cookie consent popup (4-second fade)
- **Consistent Navigation** — Home button, user info, and logout across all protected pages

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3, Flask 3.1 |
| ORM | Flask-SQLAlchemy 3.1 |
| Sessions | Flask-Session (filesystem) |
| Security | Werkzeug password hashing |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Database | SQLite (development) |
| Deployment | Gunicorn |

---

## Project Structure

```
CyberNews/
├── web_app.py              # Main Flask application
├── requirements.txt        # Python dependencies
├── users.db                # SQLite database (auto-created)
├── static/
│   ├── style.css           # Global stylesheet
│   ├── Articles.json       # News article data
│   ├── Greeting.js         # Time-based greeting logic
│   ├── Refresher.js        # Article loading logic
│   ├── CookieNoticePopup.js # Cookie banner dismissal
│   └── favicon.ico         # Site icon
└── templates/
    ├── root.html           # Landing / login page
    ├── login.html          # Dedicated login page
    ├── register.html       # Account creation
    ├── register_success.html # Post-registration confirmation
    ├── news.html           # News headlines (protected)
    ├── about.html          # About page (protected)
    ├── form.html           # Contact form (protected)
    ├── result.html         # Form submission result (protected)
    ├── admin.html          # Admin dashboard (admin only)
    └── access_denied.html  # 403-style error page
```

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/cybernews-tracker.git
cd cybernews-tracker
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
```bash
export FLASK_SECRET_KEY="your-secret-key-here"  # On Windows: set FLASK_SECRET_KEY=...
```

> **Note:** The app will raise a `ValueError` if `FLASK_SECRET_KEY` is not set.

### 5. Run the application
```bash
python web_app.py
```

The server will start at `http://127.0.0.1:5000/`.

---

## Configuration

Key Flask settings (in `web_app.py`):

| Setting | Default | Description |
|---------|---------|-------------|
| `SESSION_TYPE` | `filesystem` | Server-side session storage |
| `PERMANENT_SESSION_LIFETIME` | 2 hours | Auto-logout after inactivity |
| `SESSION_COOKIE_HTTPONLY` | `True` | Prevents XSS cookie theft |
| `SESSION_COOKIE_SECURE` | `False` | Set `True` behind HTTPS |
| `SESSION_COOKIE_SAMESITE` | `Lax` | CSRF protection |

---

## Usage

### Regular Users
1. Visit the home page and log in, or click **Sign Up** to register
2. Browse the **News** page for cybersecurity headlines
3. Use **Contact us** to submit a profile/message
4. View **About** for project info

### Administrators
1. Log in with an admin account
2. Access **Admin Dashboard** from the News page navigation
3. Promote/demote users or delete accounts as needed

---

## Security Considerations

- Passwords are hashed with **Werkzeug's `generate_password_hash`**
- Sessions expire after **2 hours** of inactivity
- Admin routes are protected by both `@login_required` and `@admin_required` decorators
- Self-deletion is handled gracefully with immediate session invalidation
- CSRF protection is recommended for production (consider Flask-WTF)

---

## License

This project is open-source and available under the [MIT License](LICENSE).

---

## Author

Made by a student of life.

© CyberNews Tracker TradeMedia
