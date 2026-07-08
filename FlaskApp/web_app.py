from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def root():
    return render_template("root.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")
    
@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/about-us")
def about():
    return render_template("about.html")

@app.route("/contact-us", methods=["GET", "POST"])
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
