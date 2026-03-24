import sqlite3

DBFILENAME = 'LostAndFound.sqlite'

# Utility function
def db_run(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()

def load(db_name = DBFILENAME):
  db_run('DROP TABLE IF EXISTS Annonce')
  db_run('DROP TABLE IF EXISTS User')
  db_run('CREATE TABLE User (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password_hash TEXT NOT NULL, email TEXT NOT NULL)')
  db_run('CREATE TABLE Annonce (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER REFERENCES User(id) ,objet TEXT NOT NULL, description TEXT NOT NULL ' \
  ', location TEXT NOT NULL, contact TEXT NOT NULL, status Boolean DEFAULT False)')

load()