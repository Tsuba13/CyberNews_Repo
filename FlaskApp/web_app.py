from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to the Route Master Home Page!"

@app.route("/status")
def status():
    return "Application is running."

@app.route("/info/<input_string>")
def info(input_string):
    current_time = datetime.now().strftime("( %d/%m/%Y - %H:%M )")
    return f"You entered '{input_string}' at {current_time}"

@app.route("/greet/<name>")
def greet(name):
    return f"Hey, {name}! Weclome back in our server :)"

@app.route("/add/<int:num1>/<int:num2>")
def add(num1, num2):
    sum = num1 + num2
    return f"The sum of {num1} and {num2} is {sum}"

if __name__ == "__main__":
    app.run(debug=True)
