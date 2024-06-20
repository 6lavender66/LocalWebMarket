from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/LocalStockMarket"
app.secret_key = 'supersecretkey'  # Sekret do sesji
mongo = PyMongo(app)

@app.route('/')
def index():
    users = mongo.db.users.find()
    return render_template('index.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    if first_name and last_name and email and password:
        user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)  # Haszowanie hasła
        mongo.db.users.insert_one({
            'id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': hashed_password  # Przechowywanie zahashowanego hasła
        })
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    print(f"Login attempt with email: {email}, password: {password}")  # Printowanie danych logowania
    user = mongo.db.users.find_one({'email': email})
    if user:
        print(f"Found user: {user}")  # Printowanie znalezionego użytkownika
        if check_password_hash(user['password'], password):  # Porównywanie zahashowanego hasła
            print("Password match")
            session['user_id'] = user['id']
            return redirect(url_for('your_account'))
        else:
            print("Password does not match")
    else:
        print("User not found")
    return redirect(url_for('index'))

@app.route('/your_account')
def your_account():
    if 'user_id' in session:
        user = mongo.db.users.find_one({'id': session['user_id']})
        if user:
            return render_template('your_account.html', user=user)
        else:
            return "User not found", 404
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
