from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps
import os

load_dotenv()

app = Flask(__name__)

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
if not app.secret_key:
    raise ValueError("FLASK_SECRET_KEY environment variable is not set")

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return f'<User {self.username}>'
        
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
                hashed_password = generate_password_hash(password)
                new_user = User(username=username, password_hash=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                return render_template("register_success.html", username=username)
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
                return redirect(url_for('news'))
        if error and request.referrer and 'root' in request.referrer:
            return redirect(url_for('root', error=error))
    return render_template("login.html", error=error)
    
@app.route("/logout")
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('root'))

@app.route("/about-us")
@login_required
def about():
    return render_template("about.html")
    
@app.route("/news")
@login_required
def news():
    return render_template("news.html")

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
