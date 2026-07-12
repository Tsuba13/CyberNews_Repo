# CyberNews

A Flask-based cybersecurity news aggregator with user authentication, live news fetching, and admin dashboard.

## Overview

CyberNews is a web application that aggregates cybersecurity news from multiple sources. It features a dual-mode news system: static articles served from a local JSON file, and live articles fetched from the [NewsAPI](https://newsapi.org) service. The app includes full user authentication, role-based access control, an admin dashboard with notification system, and a contact form.

## Features

- **User Authentication** — Secure registration and login with password hashing (Werkzeug) and server-side filesystem sessions
- **Role-Based Access Control** — Two user roles: `user` and `admin`. The first registered account automatically becomes an admin
- **Static News** — Pre-loaded cybersecurity headlines from a local JSON file
- **Live News** — Fetches real-time cybersecurity articles from NewsAPI with search, filter (by source/author), and sort capabilities
- **Article Viewer** — Dedicated article pages with metadata, optional full-content fetching from source URLs, and fallback excerpts
- **Admin Dashboard** — Manage registered users (promote/demote roles, delete accounts) with action confirmations
- **Admin Notifications** — Real-time notification system for admin users when contact form messages are submitted
- **Contact Form** — Logged-in users can submit messages; all admins are automatically notified
- **Responsive Dark Theme** — Custom CSS3 dark-mode UI with gold accent colors

## Tech Stack

| Layer        | Technology                             |
| ------------ | -------------------------------------- |
| Backend      | Python 3, Flask                        |
| ORM          | SQLAlchemy                             |
| Sessions     | Flask-Session (filesystem)             |
| Security     | Werkzeug (password hashing)            |
| Database     | SQLite (users.db + articles.db)        |
| Templating   | Jinja2                                 |
| Frontend     | Vanilla JavaScript, CSS3               |
| External API | NewsAPI                                |
| Deployment   | Render (web service + persistent disk) |
## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Tsuba13/CyberNews_Repo
   cd CyberNews_Repo
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set environment variables either locally in a `.env`  file or in the environment variables section on Render:
   ```bash
   export FLASK_SECRET_KEY="your-secret-key-here"
   export NEWS_API_KEY="your-newsapi-key-here"
   ```

4. Connect your GitHub repository to Render and deploy.

## Environment Variables

| Variable           | Required | Description                                                                                                                                               |
| ------------------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `FLASK_SECRET_KEY` | Yes      | Secret key for session management and CSRF protection                                                                                                     |
| `NEWS_API_KEY`     | No*      | API key for [NewsAPI](https://newsapi.org). Required for live news fetching. Without it, the live news page will display previously cached articles only. |

## Database

The application uses two SQLite databases:
- **`users.db`** — Stores user accounts, roles, and creation timestamps
- **`articles.db`** — Stores fetched live news articles with metadata

Both databases are auto-created on first run via `db.create_all()`. On Render, ensure `/var/data/` is mounted to a persistent disk.

## Routes

| Route | Method | Access | Description |
|-------|--------|--------|-------------|
| `/` | GET | Public | Homepage (shows login form or welcome back) |
| `/register` | GET/POST | Public | Create a new account |
| `/login` | GET/POST | Public | Log in to existing account |
| `/logout` | GET | Logged-in | Clear session and log out |
| `/news` | GET | Logged-in | Static news from JSON file |
| `/news-live` | GET/POST | Logged-in | Live news with search/filter |
| `/article/<id>` | GET | Logged-in | View single article |
| `/article/<id>/fetch-content` | POST | Logged-in | Scrape full article text from source |
| `/contact-us` | GET/POST | Logged-in | Contact form (notifies admins on submit) |
| `/about-us` | GET | Logged-in | About / credits page |
| `/admin_dashboard` | GET | Admin only | User management table |
| `/admin/toggle-role/<id>` | POST | Admin only | Promote/demote a user |
| `/admin/delete-user/<id>` | POST | Admin only | Delete a user account |
| `/admin/notifications` | GET | Admin only | View all notifications |
| `/admin/notifications/<id>/read` | POST | Admin only | Mark notification as read |
| `/admin/notifications/mark-all-read` | POST | Admin only | Mark all as read |
| `/admin/notifications/<id>/delete` | POST | Admin only | Delete a notification |
| `/access_denied` | GET | Logged-in | Unauthorized access page |

## Admin Features

- **User Management**: View all registered users, toggle roles between `user` and `admin`, delete accounts (with self-protection)
- **Notifications**: Receive automatic notifications when a contact form is submitted. Notifications support marking as read (individual or bulk) and deletion.
- **Badge Indicators**: Unread notification count appears in the footer across all pages when logged in as admin.

## Security Notes

- Passwords are hashed with Werkzeug's `generate_password_hash`
- Sessions are server-side (filesystem) with 2-hour lifetime
- Session cookies are `HttpOnly`, `Secure`, and `SameSite=Lax`
- Admin routes are protected by `@admin_required` decorator
- Self-deletion from admin dashboard immediately logs the admin out
- Article content fetching uses a realistic browser User-Agent to reduce blocking

## License

This project was created for **educational purposes**.

**Author:** Mhd Najeeb Mshaweh  
**Teaching body:** Cybersteps

---

*Powered by NewsAPI.org*
