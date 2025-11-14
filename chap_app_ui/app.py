from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def login():
    return render_template("login.html", title="Đăng nhập")

@app.route("/register")
def register():
    return render_template("register.html", title="Đăng ký")

if __name__ == "__main__":
    app.run(debug=True)
