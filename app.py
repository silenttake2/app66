from flask import Flask, request, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os
import urllib.parse

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your_secret_key")

# ================================
# RAILWAY POSTGRES DATABASE
# ================================
username = urllib.parse.quote_plus(os.getenv("PGUSER", ""))
password = urllib.parse.quote_plus(os.getenv("PGPASSWORD", ""))
host = os.getenv("PGHOST", "")
port = os.getenv("PGPORT", "5432")
database = os.getenv("PGDATABASE", "")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{username}:{password}@{host}:{port}/{database}"
)

db = SQLAlchemy(app)

# ================================
# Model for notes
# ================================
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user = db.Column(db.String(50), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Admin user credentials
ADMIN_PASSWORD = '5170'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == '5071':
            session['user'] = 'silent'
        elif password == 'missrock':
            session['user'] = 'raifa'
        elif password == ADMIN_PASSWORD:
            session['user'] = 'admin'
        else:
            return 'Invalid password'
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    notes = Note.query.all()
    return render_template('index.html', notes=notes, user=session['user'])

@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    content = request.form['content']
    user = session['user']
    new_note = Note(content=content, user=user)
    db.session.add(new_note)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_note/<int:id>', methods=['POST'])
@admin_required
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
