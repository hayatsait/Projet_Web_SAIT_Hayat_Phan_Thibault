from flask import Flask, session, request, redirect, url_for, render_template, flash
from functools import wraps
import random
import smtplib
from email.mime.text import MIMEText
import os
import data_model as model
import secrets

app = Flask(__name__)
app.secret_key = "4c7f49019d9cea50d56f5da6f8dd4412a17f84386cda0b84e987679e0a2c6fc7"


EMAIL_ADDRESS = "amufound.noreply@gmail.com"
EMAIL_APP_PASSWORD = "xvgq zrbb abwe bzys"


@app.context_processor
def inject_user():
    user = None
    if "user_id" in session:
        user = model.getUserById(session["user_id"])

    return {
        "is_logged_in": "user_id" in session,
        "current_username": user["username"] if user else None,
        "current_user_email": user["email"] if user else None,
    }


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
    return render_template("acceuil.html")
   

# UNE SEULE PAGE pour login + signup
@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
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


@app.route("/register", methods=["POST"])
def register_post():
    username = request.form["username"].strip()
    email = request.form["email"].strip().lower()
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    if not username or not email or not password or not confirm_password:
        flash("Veuillez remplir tous les champs.")
        return redirect(url_for("login"))

    if password != confirm_password:
        flash("Les mots de passe ne correspondent pas.")
        return redirect(url_for("login"))

    if model.getUserByEmail(email):
        flash("Cet email existe déjà.")
        return redirect(url_for("login"))

    code = generate_code()
    model.save_verification_code(email, code)

    session["pending_username"] = username
    session["pending_email"] = email
    session["pending_password"] = password

    try:
        send_verification_email(email, code)
    except Exception as e:
        print("Erreur email :", e)
        flash("Erreur lors de l'envoi du code.")
        return redirect(url_for("login"))

    return redirect(url_for("verify_email_page"))



@app.route("/verify-email", methods=["GET"])
def verify_email_page():
    if "pending_email" not in session:
        return redirect(url_for("login"))
    return render_template("verify_email.html", email=session["pending_email"])


@app.route("/verify-email", methods=["POST"])
def verify_email_post():
    code_entered = request.form["code"].strip()
    email = session.get("pending_email")
    username = session.get("pending_username")
    password = session.get("pending_password")

    if not email or not username or not password:
        flash("Session expirée.")
        return redirect(url_for("login"))

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


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))


# =========================
# ANNONCES
# =========================

@app.route("/annonces")
def annonces():
    page = request.args.get("page", default=1, type=int)
    mode = request.args.get("mode", default="perdu", type=str)
    query = request.args.get("q", default="", type=str).strip()

    objets = request.args.getlist("objet")
    locations = request.args.getlist("location")

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


@app.route("/nouvelle_annonce", methods=["POST"])
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


@app.route("/annonces/<int:id>/confirm", methods=["POST"])
@login_required
def validation(id):
    model.confirmation(id)
    return redirect(url_for("annonces"))

@app.route("/profil")
@login_required
def profil():
    user = model.getUserById(session["user_id"])
    return render_template("profil.html", user=user)


@app.route("/profil/update-username", methods=["POST"])
@login_required
def update_username():
    new_username = request.form["username"].strip()
    user_id = session["user_id"]

    if not new_username:
        flash("Le nom d'utilisateur ne peut pas être vide.")
        return redirect(url_for("profil"))

    model.update_username(user_id, new_username)
    session["username"] = new_username
    flash("Nom d'utilisateur mis à jour avec succès.")
    return redirect(url_for("profil"))


@app.route("/profil/update-email", methods=["POST"])
@login_required
def update_email():
    new_email = request.form["email"].strip().lower()
    user_id = session["user_id"]

    if not new_email:
        flash("L'adresse email ne peut pas être vide.")
        return redirect(url_for("profil"))

    existing_user = model.getUserByEmail(new_email)
    if existing_user and existing_user["id"] != user_id:
        flash("Cet email est déjà utilisé.")
        return redirect(url_for("profil"))

    model.update_email(user_id, new_email)
    flash("Adresse email mise à jour avec succès.")
    return redirect(url_for("profil"))


@app.route("/profil/update-password", methods=["POST"])
@login_required
def update_password():
    user_id = session["user_id"]
    old_password = request.form["old_password"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    user = model.getUserById(user_id)

    if not old_password or not new_password or not confirm_password:
        flash("Veuillez remplir tous les champs du mot de passe.")
        return redirect(url_for("profil"))

    if not model.check_user_password(user["email"], old_password):
        flash("Ancien mot de passe incorrect.")
        return redirect(url_for("profil"))

    if new_password != confirm_password:
        flash("Les nouveaux mots de passe ne correspondent pas.")
        return redirect(url_for("profil"))

    model.update_password(user_id, new_password)
    flash("Votre mot de passe a été mis à jour avec succès.")
    return redirect(url_for("profil"))


@app.route("/profil/delete-account", methods=["POST"])
@login_required
def delete_account():
    user_id = session["user_id"]

    model.delete_user_account(user_id)
    session.clear()

    flash("Votre compte a été supprimé.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)