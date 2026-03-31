import sqlite3
import math
from werkzeug.security import check_password_hash


DBFILENAME = 'LostAndFound.sqlite'

# Utility functions
def db_fetch(query, args=(), all=False, db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    # to allow access to columns by name in res
    conn.row_factory = sqlite3.Row 
    cur = conn.execute(query, args)
    # convert to a python dictionary for convenience
    if all:
      res = cur.fetchall()
      if res:
        res = [dict(e) for e in res]
      else:
        res = []
    else:
      res = cur.fetchone()
      if res:
        res = dict(res)
  return res

def db_insert(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()
    return cur.lastrowid


def db_run(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()


def db_update(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()
    return cur.rowcount
  
def search(query="", page=1):
  num_per_page = 32
  # on utiliser l'opérateur SQL LIKE pour rechercher dans le titre 
  res = db_fetch('SELECT count(*) FROM Annonces WHERE objet LIKE ?',
                       ('%' + query + '%',))
  num_found = res['count(*)']
  results = db_fetch('SELECT id as entry, title, img FROM recipe WHERE title LIKE ? ORDER BY id LIMIT ? OFFSET ?',
                     ('%' + query + '%', num_per_page, (page - 1) * num_per_page), all=True)
  return {
    'results': results,
    'num_found': num_found, 
    'query': query,
    'next_page': page + 1,
    'page': page,
    'num_pages': math.ceil(float(num_found) / float(num_per_page))
  }

def login(name, password, db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            'SELECT id, username, password_hash FROM user WHERE username = ?',
            (name,)
        )
        row = cur.fetchone()

    if row is None:
        return -1

    if check_password_hash(row['password_hash'], password):
        return row['id']

    return -1

def new_user(email, name, password):
  new = db_insert('INSERT INTO User (email, username, password_hash) VALUES(? , ?, ?)', (email, name, password))
  return new

def getName(id):
    name = db_fetch('SELECT * From User Where id =?',(id))
    return name['username']

def new_announcement(user_id, item, desc, loc, cont):
  new = db_insert('INSERT INTO Annonce (user_id, objet, description, location, contact, status)', (user_id, item, desc, loc, cont, False))
  return new

def confirmation(id):
  found = db_update('UPDATE Annonce SET status = True WHERE id = ?', (id))
  return found

def getUserById(user_id):
  user = db_fetch('SELECT * FROM User WHERE id = ?', (user_id))
  return user

def getUserByEmail(email):
  user = db_fetch('SELECT * FROM User WHERE email = ?', (email))
  return user

def getAllActive():
  return db_fetch('SELECT * FROM Annonce Where status = False')

def getAnnouncementByID(objID):
  Anon = db_fetch('SELECT * FROM Annonce Where id = ?',(objID))
  return Anon

def getUserbyAnnonceId(objID):
  id = db_fetch('SELECT user_id FROM Annonce Where id = ?',(objID))
  user = user = db_fetch('SELECT * FROM User WHERE id = ?', (id))
  return user
