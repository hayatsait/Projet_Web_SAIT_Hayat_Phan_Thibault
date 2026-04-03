from flask import Flask, session, request, redirect, url_for, render_template, flash
from functools import wraps
import random
import smtplib
from email.mime.text import MIMEText
import os
import data_model as model

app = Flask(__name__)
app.secret_key = "change_this_secret_key"


EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "tonemail@gmail.com")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD", "ton_mot_de_passe_app")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def generate_code():
    return str(random.randint(100000, 999999))


def send_verification_email(to_email, code):
    subject = "Code de vérification - LostAndFound"
    body = f"Votre code de vérification est : {code}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        smtp.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())


# =========================
# PAGES PRINCIPALES
# =========================

@app.route("/")
def index():
    if "username" in session:
        return render_template("acceuil.html", logged_in=True, username=session["username"])
    return render_template("acceuil.html", logged_in=False)


@app.route("/login")
def login():
    return render_template("login.html")


@app.post("/login")
def login_post():
    email = request.form["email"].strip().lower()
    password = request.form["password"]

    user = model.login(email, password)

    if user is None:
        flash("Email ou mot de passe incorrect, ou email non vérifié.")
        return redirect(url_for("login"))

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return redirect(url_for("index"))


@app.route("/register")
def register():
    return render_template("register.html")


@app.post("/register")
def register_post():
    name = request.form["username"].strip()
    email = request.form["email"].strip().lower()
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    if not name or not email or not password or not confirm_password:
        flash("Veuillez remplir tous les champs.")
        return redirect(url_for("register"))

    if password != confirm_password:
        flash("Les mots de passe ne correspondent pas.")
        return redirect(url_for("register"))

    if model.getUserByEmail(email):
        flash("Cet email existe déjà.")
        return redirect(url_for("register"))

    code = generate_code()
    model.save_verification_code(email, code)

    session["pending_username"] = name
    session["pending_email"] = email
    session["pending_password"] = password

    try:
        send_verification_email(email, code)
    except Exception as e:
        print("Erreur email :", e)
        flash("Erreur lors de l'envoi du code.")
        return redirect(url_for("register"))

    return redirect(url_for("verify_email_page"))


@app.route("/verify-email")
def verify_email_page():
    if "pending_email" not in session:
        return redirect(url_for("register"))
    return render_template("verify_email.html", email=session["pending_email"])


@app.post("/verify-email")
def verify_email_post():
    code_entered = request.form["code"].strip()
    email = session.get("pending_email")
    username = session.get("pending_username")
    password = session.get("pending_password")

    if not email or not username or not password:
        flash("Session expirée.")
        return redirect(url_for("register"))

    saved = model.get_verification_code(email)

    if saved is None or saved["code"] != code_entered:
        flash("Code incorrect.")
        return redirect(url_for("verify_email_page"))

    user_id = model.new_user(email, username, password)
    model.delete_verification_code(email)

    session.pop("pending_email", None)
    session.pop("pending_username", None)
    session.pop("pending_password", None)

    session["user_id"] = user_id
    session["username"] = username

    flash("Compte créé avec succès.")
    return redirect(url_for("index"))


@app.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))


# =========================
# ANNONCES + FILTRAGE FLASK
# =========================

@app.route("/annonces")
def annonces():
    page = request.args.get("page", default=1, type=int)
    mode = request.args.get("mode", default="perdu", type=str)
    query = request.args.get("q", default="", type=str).strip()

    objets = request.args.getlist("objet")
    locations = request.args.getlist("location")

    # sécurité simple
    if mode not in ["perdu", "trouve"]:
        mode = "perdu"

    found = model.search_annonces(
        mode=mode,
        objets=objets,
        locations=locations,
        query=query,
        page=page
    )

    return render_template("annonces.html", found=found)


@app.route("/nouvelle_annonce")
@login_required
def nouvelle_annonce():
    return render_template("nouvelle_annonce.html")


@app.post("/nouvelle_annonce")
@login_required
def add_annonce():
    user_id = session["user_id"]
    annonce_type = request.form["type"]
    obj = request.form["objet"]
    desc = request.form["description"]
    loc = request.form["location"]
    img = request.form.get("image", "")
    cont = request.form["email"]

    model.new_announcement(user_id, annonce_type, obj, desc, loc, img, cont)
    return redirect(url_for("annonces", mode=annonce_type))


@app.post("/annonces/<int:id>/confirm")
@login_required
def validation(id):
    model.confirmation(id)
    return redirect(url_for("annonces"))


if __name__ == "__main__":
    app.run(debug=True)