from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request , session, redirect, url_for

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = "mysecretkey"
db = SQLAlchemy(app)
#Create Model
class Users(db.Model):
    email = db.Column(db.String(50),primary_key = True)
    password = db.Column(db.String(50),nullable = False)
    date_addit = db.Column(db.DateTime, default = datetime.utcnow)

@app.route("/")
def home():
    if session.get("email"):
        text = "Products"
        link = "/products"
    else:
        text = "Create Account"
        link = "/signup"
    return render_template("index.html",text = text,link = link)

@app.route("/signup",methods = ["POST","GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        verifypassword = request.form["verify"]
        print(email,password)
        if password == verifypassword:
            new_user = Users(email = email, password = password)
            db.session.add(new_user)
            db.session.commit()
        else:
            print("Passwords dont match")
    return render_template("signup.html")

@app.route("/login",methods = ["POST","GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        current_user = Users.query.filter_by(email=email).first()   
        if current_user and current_user.password == password:
            session["email"] = current_user.email
            return redirect(url_for("products"))
        else:
            print("Wrong information")
    return render_template("login.html")

@app.route("/products")
def products():
    return render_template("products.html")

@app.route("/profile")
def profile():
    if not session.get("email"):
        return redirect(url_for("login"))
    current_user = Users.query.filter_by(email = session["email"]).first()
    return render_template("profile.html",current_user = current_user)

    

@app.route("/logout")
def logout():
    session.pop("email",None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)