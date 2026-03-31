from flask import Flask, session, Response, request, redirect, url_for, render_template
import data_model as model
from functools import wraps

app = Flask(__name__)

app.secret_key = b'f7e465ed26d683087740162fdaf5d91c2c1b116e898d641109423e689b2a0182'

def login_required(f) :
   @wraps(f)
   def decorated_function(*args, **kwargs):
        if not('user_id' in session):
            return "unauthorized", 401
        else:
            return f(*args, **kwargs)
   return decorated_function

###########################################################################
# Route du sites (méthodes GET)
###########################################################################

#page d'accueil

@app.get('/')
def home():
  if 'username' in session:
    username = session['username']
    return render_template('accueil.html',logged_in=True, username=username)
  else:
    return render_template('accueil.html',logged_in=False, username=None)

# Retourne les résultats de la recherche à partir de la requête "query"
@app.get('/search')
def search():
  if 'page' in request.args:
    page = int(request.args["page"])
  else:
    page = 1
  if 'query' in request.args:
    query = request.args["query"]
  else:
    query = ""
  found = model.search(query, page)
  return render_template('search.html', found=found)

@app.get('/annonces')
@login_required
def toAnnonce():
   annonces = model.getAllActive() # Liste de toutes les annonces valides
   return render_template('annonce.html', annonces = annonces)

@app.get('/login')
def tologin():
   return render_template('login.html')

@app.get('/register')
def toregister():
   return render_template('register.html')

@app.get('/annonces/<id>')
@login_required
def toAnnonce(id):
   annonce = model.getAnnouncementByID(id)
   user = model.getUserbyAnnonceId(id)
   return render_template('annonce.html', annonce = annonce, user = user)

@app.get('/annonces/<id>/claim')
@login_required
def toClaim(id):
   annonce = model.getAnnouncementByID(id)
   return render_template('ClaimedConfirmation.html', annonce = annonce )

@app.get('/annonces/new')
@login_required
def toCreateAnnonce():
   return render_template('NewAnnonce.html')

@app.get('/logout')
@login_required
def logout():
  session.clear()
  return redirect('/')

###########################################################################
# actions du site (méthodes POST)
###########################################################################

@app.post('/login')
def login_post():
    email = request.form['email']
    password = request.form['password']

    user_id = model.login(email, password)

    if user_id == -1:
        return redirect(url_for('tologin'))

    name = model.getName(user_id)
    session['user_id'] = user_id
    session['user_name'] = name
    return redirect(url_for('home'))

@app.post('/register')
def register_post():
    name = request.form['username']
    email = request.form['email']
    password = request.form['password']
    model.new_user(email, name, password)
    return redirect('/')

@app.post('/annonces/new')
@login_required
def addAnnonces():
    user_id = session['user_id']
    obj = request.form['object']
    desc = request.form['description']
    loc = request.form['location']
    cont = request.form['contact']
    model.new_announcement(user_id, obj, desc, loc, cont)
    return redirect('/annonces')

@app.post('/annonces/<id>/claim')
@login_required
def Validation():
   idObj = f"annonces {id}"
   model.confirmation(idObj)
   return redirect('/annonces')

if __name__=="__main__":
    app.run(port = 5000 ,debug="true")