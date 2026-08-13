from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request , session, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.secret_key = "mysecretkey"
db = SQLAlchemy(app)
#Create Model
class Users(db.Model):
    email = db.Column(db.String(50),primary_key = True)
    password = db.Column(db.String(50),nullable = False)
    date_addit = db.Column(db.DateTime, default = datetime.utcnow)
    verified = db.Column(db.Boolean, default = False)
    role = db.Column(db.String(10), default = "Guest") #Admin , User , Guest
    image = db.Column(db.String(55), default = "imgdefault.png")

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    description = db.Column(db.String(40), nullable = False)
    price = db.Column(db.Float, nullable = False)
    image = db.Column(db.String(55))
    date_addit = db.Column(db.DateTime, default = datetime.utcnow)


UPLOAD_FOLDER = os.path.join("static", "products_img")
PROFILE_UPLOAD_FOLDER = os.path.join("static", "profile_img")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


@app.route("/")
@app.route("/home")
def home():
    if session.get("email"):
        text = "Products"
        link = "/products"
    else:
        text = "Create Account"
        link = "/signup"
    return render_template("index.html",text = text,link = link,condition = "home",logged = session.get("email"), role = session.get("role"))

@app.route("/signup",methods = ["POST","GET"])
def signup():
    current_user = None
    if session.get("email"):
        current_user = Users.query.filter_by(email = session.get("email")).first()
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        verifypassword = request.form["verify"]
        if password == verifypassword:
            existing_user = Users.query.filter_by(email = email).first()
            if existing_user :
                flash("Email Already Exist","danger")
                return render_template("signup.html",condition = "signup",logged = session.get("email") , role = session.get("role"), current_user = current_user)
            new_user = Users(email = email, password = password)
            db.session.add(new_user)
            db.session.commit()
            flash("Account Created Successfully", "success")
            return redirect(url_for("login"))
        else:
            flash("Passwords Dont Match", "danger")  # ===> Flash message
    return render_template("signup.html",condition = "signup",logged = session.get("email") , role = session.get("role"),current_user = current_user)

@app.route("/login",methods = ["POST","GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        current_user = Users.query.filter_by(email=email).first()   
        if current_user and current_user.password == password:
            session["email"] = current_user.email
            session["role"] = current_user.role
            return redirect(url_for("products"))
        else:
            flash("Wrong email or password.", "danger")  # ===> Flash message
    return render_template("login.html",condition = "login", logged = session.get("email") , role = session.get("role"))

@app.route("/products")
def products():
    all_products = Product.query.all()
    return render_template("products.html", products = all_products,condition = "products",logged = session.get("email") , role = session.get("role"))

@app.route("/profile", methods = ["POST","GET"])
def profile():
    if not session.get("email"):
        return redirect(url_for("login"))
    current_user = Users.query.filter_by(email = session["email"]).first()
    if request.method == "POST":
        img_file = request.files.get("image")
        if img_file and img_file.filename != "" and allowed_file(img_file.filename):
            extension = img_file.filename.rsplit(".", 1)[1].lower()
            filename = secure_filename(f"{current_user.email}.{extension}")
            os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)
            img_file.save(os.path.join(PROFILE_UPLOAD_FOLDER, filename))
            current_user.image = filename
            db.session.commit()
            flash("Image Updated","success")
        else:
            flash("Only Allowed Extensions .png, .jpg, .jpeg")
            return redirect(url_for("profile"))
    return render_template("profile.html",current_user = current_user,condition = "profile",logged = session.get("email") , role = session.get("role"))

@app.route("/logout")
def logout():
    session.pop("email",None)
    return redirect(url_for("home"))

@app.route("/admin", methods = ["POST","GET"])
def admin():
    if not session.get("email"):
        return redirect(url_for("login"))
    current_user = Users.query.filter_by(email = session["email"]).first()
    if current_user and current_user.role == "Admin":
        if request.method == "POST":
            name = request.form["name"]
            price = request.form["price"]
            description = request.form["description"]
            image_file = request.files.get("image")
            if not image_file or image_file.filename == "":
                   return "Πρέπει να επιλέξεις μια εικόνα.", 400
            if not allowed_file(image_file.filename):
                return "Επιτρέπονται μόνο αρχεία .png, .jpg, .jpeg", 400
            extension = image_file.filename.rsplit(".", 1)[1].lower()
            new_product = Product(name = name, price = float(price), description = description)
            db.session.add(new_product)
            db.session.commit()
            image_filename = secure_filename(f"{new_product.id}.{extension}")
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(UPLOAD_FOLDER, image_filename))
            new_product.image = image_filename
            db.session.commit()
    else:
        print("No Access")
    return render_template("admin.html",logged = session.get("email"),condition = "admin")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)