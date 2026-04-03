import sqlite3
import math
from werkzeug.security import check_password_hash, generate_password_hash

DBFILENAME = "LostAndFound.sqlite"


# =========================
# OUTILS DB
# =========================

def db_fetch(query, args=(), all=False, db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)

        if all:
            rows = cur.fetchall()
            return [dict(row) for row in rows]

        row = cur.fetchone()
        return dict(row) if row else None


def db_insert(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.lastrowid


def db_update(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.rowcount


def db_run(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        conn.execute(query, args)
        conn.commit()


# =========================
# AUTHENTIFICATION
# =========================

def getUserByEmail(email):
    return db_fetch("SELECT * FROM User WHERE email = ?", (email,))


def getUserById(user_id):
    return db_fetch("SELECT * FROM User WHERE id = ?", (user_id,))


def getName(user_id):
    user = getUserById(user_id)
    return user["username"] if user else None


def getNamebyEmail(email):
    user = getUserByEmail(email)
    return user["username"] if user else None


def login(email, password, db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM User WHERE email = ?", (email,))
        row = cur.fetchone()

    if row is None:
        return None

    if row["is_verified"] != 1:
        return None

    if check_password_hash(row["password_hash"], password):
        return dict(row)

    return None


def new_user(email, name, password):
    password_hash = generate_password_hash(password)
    return db_insert(
        "INSERT INTO User (email, username, password_hash, is_verified) VALUES (?, ?, ?, 1)",
        (email, name, password_hash)
    )


def save_verification_code(email, code):
    db_run("DELETE FROM EmailVerification WHERE email = ?", (email,))
    return db_insert(
        "INSERT INTO EmailVerification (email, code) VALUES (?, ?)",
        (email, code)
    )


def get_verification_code(email):
    return db_fetch(
        "SELECT * FROM EmailVerification WHERE email = ? ORDER BY id DESC LIMIT 1",
        (email,)
    )


def delete_verification_code(email):
    return db_update("DELETE FROM EmailVerification WHERE email = ?", (email,))


# =========================
# ANNONCES
# =========================

def new_announcement(user_id, annonce_type, objet, desc, loc, img, cont):
    return db_insert("""
        INSERT INTO Annonce (user_id, type, objet, description, location, image, contact)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, annonce_type, objet, desc, loc, img, cont))


def confirmation(annonce_id):
    return db_update(
        "UPDATE Annonce SET status = 1 WHERE id = ?",
        (annonce_id,)
    )


def getAnnouncementByID(annonce_id):
    return db_fetch("SELECT * FROM Annonce WHERE id = ?", (annonce_id,))


def getUserbyAnnonceId(annonce_id):
    annonce = db_fetch("SELECT user_id FROM Annonce WHERE id = ?", (annonce_id,))
    if not annonce:
        return None
    return db_fetch("SELECT * FROM User WHERE id = ?", (annonce["user_id"],))


def getAllActive():
    return db_fetch(
        "SELECT * FROM Annonce WHERE status = 0 ORDER BY id DESC",
        all=True
    )


# =========================
# FILTRAGE FLASK
# =========================

def search_annonces(mode="perdu", objets=None, locations=None, query="", page=1):
    if objets is None:
        objets = []

    if locations is None:
        locations = []

    num_per_page = 32

    conditions = ["status = 0", "type = ?"]
    args = [mode]

    # filtre catégorie = colonne objet
    if objets:
        placeholders = ",".join(["?"] * len(objets))
        conditions.append(f"objet IN ({placeholders})")
        args.extend(objets)

    # filtre localisation = colonne location
    if locations:
        placeholders = ",".join(["?"] * len(locations))
        conditions.append(f"location IN ({placeholders})")
        args.extend(locations)

    # recherche texte
    if query:
        like_value = f"%{query}%"
        conditions.append("""
            (
                objet LIKE ?
                OR description LIKE ?
                OR location LIKE ?
            )
        """)
        args.extend([like_value, like_value, like_value])

    where_clause = " WHERE " + " AND ".join(conditions)

    count_query = f"SELECT COUNT(*) as total FROM Annonce {where_clause}"
    count_res = db_fetch(count_query, tuple(args))
    num_found = count_res["total"] if count_res else 0

    select_query = f"""
        SELECT id, type, objet, description, location, image, contact, status
        FROM Annonce
        {where_clause}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """

    select_args = args + [num_per_page, (page - 1) * num_per_page]
    results = db_fetch(select_query, tuple(select_args), all=True)

    return {
        "results": results,
        "num_found": num_found,
        "mode": mode,
        "objets": objets,
        "locations": locations,
        "query": query,
        "page": page,
        "next_page": page + 1,
        "num_pages": math.ceil(num_found / num_per_page) if num_found > 0 else 1
    }