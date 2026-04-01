from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('acceuil.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/annonces')
def annonces():
    return render_template('annonces.html')

@app.route('/nouvelle_annonce')
def nouvelle_annonce():
    return "Nouvelle annonce"

@app.route('/register')
def register():
    return "Register"

if __name__ == '__main__':
    app.run(debug=True)