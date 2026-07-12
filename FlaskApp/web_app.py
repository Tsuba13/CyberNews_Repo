from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps
import os
import urllib.request
import urllib.parse
import urllib.error
import json

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['NEWS_API_KEY'] = os.environ.get('NEWS_API_KEY')

if not app.secret_key:
    raise ValueError("FLASK_SECRET_KEY environment variable is not set")

app.config.update({
    'SESSION_TYPE': 'filesystem',
    'SESSION_FILE_DIR': '/var/data/flask_session',
    'PERMANENT_SESSION_LIFETIME': timedelta(hours=2),
    'SESSION_COOKIE_NAME': 'user_session',
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_SAMESITE': 'Lax'
})
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/data/users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if user is None:
            session.clear()
            return redirect(url_for('login'))
        session['role'] = user.role
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('access_denied'))
        return f(*args, **kwargs)
    return decorated_function

def fetch_and_save_news(api_key, page_size=100):
    if not api_key:
        return Article.query.order_by(Article.published_at.desc()).limit(page_size).all()

    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    base_url = 'https://newsapi.org/v2/everything'
    params = urllib.parse.urlencode({
        'q': 'cybersecurity OR "cyber attack" OR "data breach" OR malware OR phishing OR ransomware',
        'from': from_date,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': page_size,
        'apiKey': api_key
    })
    full_url = f"{base_url}?{params}"

    try:
        req = urllib.request.Request(full_url, headers={'User-Agent': 'CyberNews/1.0'})

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data.get('status') == 'ok':
            new_count = 0
            for item in data.get('articles', []):
                if not item.get('url') or not item.get('title'):
                    continue

                existing = Article.query.filter_by(url=item['url']).first()
                if existing:
                    continue

                try:
                    pub_date_str = item['publishedAt'].replace('Z', '+00:00')
                    pub_date = datetime.fromisoformat(pub_date_str)
                except (ValueError, AttributeError):
                    pub_date = datetime.now()

                article = Article(
                    title=item['title'] or 'No title',
                    description=item.get('description'),
                    content=item.get('content'),
                    url=item['url'],
                    image_url=item.get('urlToImage'),
                    source_name=item.get('source', {}).get('name', 'Unknown'),
                    author=item.get('author'),
                    published_at=pub_date
                )
                db.session.add(article)
                new_count += 1

            db.session.commit()
            print(f"Saved {new_count} new articles")

    except urllib.error.HTTPError as e:
        print(f"HTTP error {e.code}: {e.reason}")
        try:
            error_body = json.loads(e.read().decode('utf-8'))
            print(f"API message: {error_body.get('message')}")
        except:
            pass
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}")
    except Exception as e:
        print(f"Fetch error: {e}")
        db.session.rollback()

    return Article.query.order_by(Article.published_at.desc()).limit(page_size).all()


def fetch_full_article_content(url):
    """Fetch and extract article text from a given URL."""
    if not url:
        return None

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')

        # Try to extract article content using common patterns
        # First, try to find JSON-LD articleBody
        import re

        # Method 1: JSON-LD articleBody
        jsonld_match = re.search(r'"articleBody"\s*:\s*"([^"]+)"', html)
        if jsonld_match:
            text = jsonld_match.group(1)
            text = json.loads('"' + text + '"')
            return text.strip()

        # Method 2: Common article content containers
        content_patterns = [
            r"""<article[^>]*>(.*?)</article>""",
            r"""<div[^>]*class=["'][^"']*(?:article|content|story|post)[^"']*["'][^>]*>(.*?)</div>""",
            r"""<div[^>]*id=["'][^"']*(?:article|content|story|post)["'][^>]*>(.*?)</div>""",
        ]

        for pattern in content_patterns:
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                text = match.group(1)
                # Strip HTML tags
                text = re.sub(r'<[^>]+>', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                if len(text) > 200:
                    return text

        # Method 3: Extract all paragraph text from body
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
        if body_match:
            text = body_match.group(1)
            # Extract paragraphs
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', text, re.DOTALL | re.IGNORECASE)
            clean_paragraphs = []
            for p in paragraphs:
                p = re.sub(r'<[^>]+>', ' ', p)
                p = re.sub(r'\s+', ' ', p).strip()
                if len(p) > 50:
                    clean_paragraphs.append(p)
            if clean_paragraphs:
                return '\n\n'.join(clean_paragraphs)

        return None

    except Exception as e:
        print(f"Error fetching article content: {e}")
        return None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    def __repr__(self):
        return f'<User {self.username}>'

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(1000), unique=True, nullable=False)
    image_url = db.Column(db.String(1000), nullable=True)
    source_name = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=True)
    published_at = db.Column(db.DateTime, nullable=False)
    fetched_at = db.Column(db.DateTime, default=func.now())
    def __repr__(self):
        return f'<Article {self.title[:50]}...>'

with app.app_context():
    db.create_all()

@app.route("/")
def root():
    error = request.args.get('error')
    return render_template("root.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if not username or not password:
            error = "Username and password are required!"
        elif password != confirm_password:
            error = "Passwords do not match!"
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                error = "Username already taken!"
            else:
                if User.query.count() == 0:
                    role = 'admin'
                else:
                    role = 'user'

                hashed_password = generate_password_hash(password)
                new_user = User(username=username, password_hash=hashed_password, role=role)
                db.session.add(new_user)
                db.session.commit()
                return render_template("register_success.html", username=username, role=role)
    return render_template("register.html", error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            error = "Please enter both username and password."
        else:
            user = User.query.filter_by(username=username).first()
            if user is None or not check_password_hash(user.password_hash, password):
                error = "incorrect username or password."
            else:
                session.permanent = True
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                return redirect(url_for('news'))
        if error and request.referrer and 'root' in request.referrer:
            return redirect(url_for('root', error=error))
    return render_template("login.html", error=error)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    response = redirect(url_for('root'))
    response.delete_cookie(app.config['SESSION_COOKIE_NAME'])
    return response

@app.route("/access_denied")
@login_required
def access_denied():
    return render_template("access_denied.html")

@app.route("/admin_dashboard")
@login_required
@admin_required
def admin_dashboard():
    message = request.args.get('message')
    all_users = User.query.order_by(User.id).all()
    return render_template("admin.html", users=all_users, message=message)

@app.route("/admin/toggle-role/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def admin_toggle_role(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session.get('user_id'):
        return redirect(url_for('admin_dashboard', message='Cannot demote your own account.'))
    user.role = 'user' if user.role == 'admin' else 'admin'
    db.session.commit()
    action = 'promoted to admin' if user.role == 'admin' else 'demoted to user'
    return redirect(url_for('admin_dashboard', message=f'{user.username} {action}'))


@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def admin_delete_user(user_id):
    """Delete a user account. If deleting yourself, log out immediately."""
    user = User.query.get_or_404(user_id)
    is_self = user.id == session.get('user_id')
    username = user.username

    db.session.delete(user)
    db.session.commit()

    if is_self:
        response = redirect(url_for('root'))
        session.clear()
        response.delete_cookie(app.config['SESSION_COOKIE_NAME'])
        return response

    return redirect(url_for('admin_dashboard', message=f'Account {username} deleted'))

@app.route("/about-us")
@login_required
def about():
    return render_template("about.html")

@app.route("/news")
@login_required
def news():
    return render_template("news.html")

@app.route("/news-live", methods=["GET", "POST"])
@login_required
def news_live():
    api_key = app.config.get('NEWS_API_KEY')
    
    # POST = Refresh button (fetch from API)
    if request.method == "POST":
        if api_key:
            try:
                fetch_and_save_news(api_key)
            except Exception as e:
                print(f"FETCH ERROR: {e}")
        return redirect(url_for('news_live', **request.args))
    
    # GET = Build filtered query
    query = Article.query
    
    # Search by keyword
    search_q = request.args.get('q', '').strip()
    if search_q:
        pattern = f"%{search_q}%"
        query = query.filter(
            db.or_(Article.title.ilike(pattern), Article.description.ilike(pattern))
        )
    
    # Filter by source
    source_filter = request.args.get('source', '').strip()
    if source_filter:
        query = query.filter(Article.source_name == source_filter)
    
    # Filter by author
    author_filter = request.args.get('author', '').strip()
    if author_filter:
        query = query.filter(Article.author == author_filter)
    
    # Sort
    sort = request.args.get('sort', 'newest')
    if sort == 'oldest':
        query = query.order_by(Article.published_at.asc())
    else:
        query = query.order_by(Article.published_at.desc())
    
    # Pagination
    total_count = query.count()
    limit = request.args.get('limit', 20, type=int)
    limit = max(20, min(limit, 120))
    
    articles = query.limit(limit).all()
    has_more = total_count > limit
    next_limit = limit + 10
    
    # Dropdown options
    sources = [s[0] for s in db.session.query(Article.source_name).distinct().all() if s[0]]
    authors = [a[0] for a in db.session.query(Article.author).distinct().all() if a[0]]
    
    return render_template("news_live.html",
        articles=articles,
        total_count=total_count,
        has_more=has_more,
        next_limit=next_limit,
        sources=sources,
        authors=authors
    )

@app.route("/article/<int:article_id>")
@login_required
def view_article(article_id):
    """Display a single article by its ID."""
    article = Article.query.get_or_404(article_id)
    return render_template("article.html", article=article)

@app.route("/article/<int:article_id>/fetch-content", methods=["POST"])
@login_required
def fetch_article_content(article_id):
    """Fetch full article content from the source URL and save it."""
    article = Article.query.get_or_404(article_id)

    full_content = fetch_full_article_content(article.url)
    if full_content:
        article.content = full_content
        db.session.commit()
        message = "Full article content loaded successfully."
    else:
        message = "Could not extract full content from the source. Showing available excerpt."

    return redirect(url_for('view_article', article_id=article.id, message=message))


@app.route("/contact-us", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        form_data = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "gender": request.form.get("gender"),
            "title": request.form.get("title"),
            "message": request.form.get("message")
        }
        return render_template("result.html", data=form_data, method="POST")
    elif request.method == "GET":
        return  render_template("form.html")
    else:
     return "Bad request!", 400

if __name__ == "__main__":
    app.run(debug=False)
