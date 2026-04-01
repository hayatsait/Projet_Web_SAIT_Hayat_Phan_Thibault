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

@app.route('/')
def index():  
    if 'username' in session:
        username = session['username']
        return render_template('acceuil.html',logged_in=True)
    else:
        return render_template('acceuil.html',logged_in=False)


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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/annonces')
def annonces():
    return "Page annonces"

@app.route('/nouvelle_annonce')
@login_required
def nouvelle_annonce():
    return "Nouvelle annonce"

@app.route('/register')
def register():
    return "Register"

@app.post('/logout')
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
        return redirect(url_for('login'))
    
    session.clear()
    name = model.getNamebyEmail(email)
    session['user_id'] = user_id
    session['username'] = name
    return redirect('/')

@app.post('/register')
def register_post():
    name = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirmPassword = request.form['confirm_password']
    if(password == confirmPassword):
        model.new_user(email, name, password)
        return redirect('/')
    else:
       return redirect('/register')

@app.post('/nouvelle_annonce')
@login_required
def addAnnonces():
    user_id = session['user_id']
    obj = request.form['objet']
    desc = request.form['description']
    loc = request.form['location']
    img = request.form['image']
    cont = request.form['email']
    model.new_announcement(user_id, obj, desc, loc, img, cont)
    return redirect('/annonces')

#appliqué cette méthode pour le bouton confirmation
@app.post('/annonces')
@login_required
def Validation(id):
   model.confirmation(id)
   return redirect('/annonces')


if __name__ == '__main__':
    app.run(debug=True)