import sqlite3

DBFILENAME = "LostAndFound.sqlite"


def db_run(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        conn.execute(query, args)
        conn.commit()


def load(db_name=DBFILENAME):
    db_run("DROP TABLE IF EXISTS EmailVerification", db_name=db_name)
    db_run("DROP TABLE IF EXISTS Annonce", db_name=db_name)
    db_run("DROP TABLE IF EXISTS User", db_name=db_name)

    db_run("""
        CREATE TABLE User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            is_verified INTEGER NOT NULL DEFAULT 0
        )
    """, db_name=db_name)

    db_run("""
        CREATE TABLE Annonce (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES User(id),
            type TEXT NOT NULL CHECK(type IN ('perdu', 'trouve')),
            objet TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            image TEXT,
            contact TEXT NOT NULL,
            status INTEGER NOT NULL DEFAULT 0
        )
    """, db_name=db_name)

    db_run("""
        CREATE TABLE EmailVerification (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """, db_name=db_name)


if __name__ == "__main__":
    load()
    print("Base créée avec succès.")