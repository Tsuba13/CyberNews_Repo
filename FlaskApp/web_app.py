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
import requests

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['NEWS_API_KEY'] = os.environ.get('NEWS_API_KEY')

if not app.secret_key:
    raise ValueError("FLASK_SECRET_KEY environment variable is not set")

app.config.update({
    'SESSION_TYPE': 'filesystem',
    'PERMANENT_SESSION_LIFETIME': timedelta(hours=2),
    'SESSION_COOKIE_NAME': 'user_session',
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SECURE': False,
    'SESSION_COOKIE_SAMESITE': 'Lax'
})
Session(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('access_denied'))
        return f(*args, **kwargs)
    return decorated_function

def fetch_and_save_news(api_key, page_size=20):
    if not api_key:
        return Article.query.order_by(Article.published_at.desc()).limit(page_size).all()
    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': 'cybersecurity OR "cyber attack" OR "data breach" OR malware OR phishing OR ransomware',
        'from': from_date,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': page_size,
        'apiKey': api_key
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get('status') == 'ok':
            new_count = 0
            for item in data.get('articles', []):
                existing = Article.query.filter_by(url=item['url']).first()
                if existing:
                    continue
                pub_date = datetime.fromisoformat(item['publishedAt'].replace('Z', '+00:00'))
                article = Article(
                    title=item['title'] or 'No title',
                    description=item['description'],
                    url=item['url'],
                    image_url=item.get('urlToImage'),
                    source_name=item['source']['name'],
                    author=item.get('author'),
                    published_at=pub_date
                )
                db.session.add(article)
                new_count += 1
            db.session.commit()
            print(f"Saved {new_count} new articles")
    except Exception as e:
        print(f"Fetch error: {e}")
        db.session.rollback()
    return Article.query.order_by(Article.published_at.desc()).limit(page_size).all()

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
    
    if request.method == "POST":
        if api_key:
            try:
                # Your fetch code here
                fetch_and_save_news(api_key)
            except Exception as e:
                print(f"FETCH ERROR: {e}")  # Check Render logs for this
        else:
            print("ERROR: No API key in app.config")
    
    articles = Article.query.order_by(Article.published_at.desc()).limit(20).all()
    return render_template("news_live.html", articles=articles)

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
    app.run(debug=True)
