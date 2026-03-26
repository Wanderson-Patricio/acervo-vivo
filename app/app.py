from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/authenticate")
def authenticate():
    return render_template("authenticate.html")

if __name__ == "__main__":
    app.run(debug=True)
