from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://Egzaminator:1234@cluster0.kxie8rk.mongodb.net/StockDB?retryWrites=true&w=majority"
app.secret_key = 'supersecretkey'
mongo = PyMongo(app)

# sprawdzenie, czy połączenie z bazą danych zostało nawiązane
if mongo.db is None:
    print("Nie udało się nawiązać połączenia z MongoDB. Sprawdź URI połączenia.")
else:
    print("Połączenie z MongoDB nawiązane pomyślnie.")

@app.route('/')
def index():
    # wyświetla stronę główną z formularzami logowania i rejestracji
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    # pobiera dane z formularza rejestracyjnego
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')

    # sprawdza, czy wszystkie pola są wypełnione
    if first_name and last_name and email and password:
        user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)

        # dodaje nowego użytkownika do bazy danych
        mongo.db.users.insert_one({
            'id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': hashed_password,
            'funds': 10000.0,
            'portfolio': []
        })

    # przekierowuje na stronę główną po rejestracji
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    # pobiera dane z formularza logowania
    email = request.form.get('email')
    password = request.form.get('password')

    # znajduje użytkownika w bazie danych na podstawie email
    user = mongo.db.users.find_one({'email': email})

    # sprawdza poprawność hasła
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        return redirect(url_for('account'))
    
    # w przypadku błędu logowania, wyświetla komunikat błędu
    return render_template('index.html', error="Złe hasło lub email")

@app.route('/account')
def account():
    # sprawdza, czy użytkownik jest zalogowany
    if 'user_id' in session:
        user = mongo.db.users.find_one({'id': session['user_id']})
        stocks = mongo.db.stocks.find()
        return render_template('account.html', user=user, stocks=stocks)
    
    # przekierowuje na stronę główną, jeśli użytkownik nie jest zalogowany
    return redirect(url_for('index'))

@app.route('/market')
def market():
    # sprawdza, czy użytkownik jest zalogowany
    if 'user_id' in session:
        user = mongo.db.users.find_one({'id': session['user_id']})
        stocks = mongo.db.stocks.find()
        return render_template('market.html', stocks=stocks, user=user)
    
    # przekierowuje na stronę główną, jeśli użytkownik nie jest zalogowany
    return redirect(url_for('index'))

@app.route('/buy_stock', methods=['POST'])
def buy_stock():
    # sprawdza, czy użytkownik jest zalogowany
    if 'user_id' in session:
        stock_id = request.form.get('stock_id')
        quantity = int(request.form.get('quantity'))

        # znajduje akcje i użytkownika w bazie danych
        stock = mongo.db.stocks.find_one({'id': stock_id})
        user = mongo.db.users.find_one({'id': session['user_id']})

        # oblicza łączną cenę zakupu
        total_price = stock['price'] * quantity
        
        # sprawdza, czy użytkownik ma wystarczające środki na zakup
        if user['funds'] >= total_price:
            # aktualizuje dane użytkownika i dodaje akcje do jego portfela
            mongo.db.users.update_one(
                {'id': session['user_id']},
                {
                    '$inc': {'funds': -total_price},
                    '$push': {'portfolio': {'stock_id': stock_id, 'quantity': quantity}}
                }
            )

            # rejestruje transakcję zakupu w bazie danych
            mongo.db.transactions.insert_one({
                'user_id': session['user_id'],
                'stock_id': stock_id,
                'quantity': quantity,
                'price': stock['price'],
                'type': 'buy',
                'timestamp': datetime.utcnow()
            })

            # przekierowuje na stronę rynku
            return redirect(url_for('market'))

    # przekierowuje na stronę rynku, jeśli niepowodzenie
    return redirect(url_for('market'))

@app.route('/sell_stock', methods=['POST'])
def sell_stock():
    # sprawdza, czy użytkownik jest zalogowany
    if 'user_id' in session:
        stock_id = request.form.get('stock_id')
        quantity = int(request.form.get('quantity'))

        # znajduje użytkownika i sprawdza, czy posiada akcje w portfelu
        user = mongo.db.users.find_one({'id': session['user_id']})
        portfolio_item = next((item for item in user['portfolio'] if item['stock_id'] == stock_id), None)
        
        # sprawdza, czy użytkownik ma wystarczającą ilość akcji do sprzedaży
        if portfolio_item and portfolio_item['quantity'] >= quantity:
            total_price = quantity * mongo.db.stocks.find_one({'id': stock_id})['price']

            # aktualizuje dane użytkownika i usuwa akcje z jego portfela
            mongo.db.users.update_one(
                {'id': session['user_id']},
                {
                    '$inc': {'funds': total_price},
                    '$pull': {'portfolio': {'stock_id': stock_id}},
                }
            )

            # jeśli pozostało więcej akcji, dodaje je z powrotem do portfela
            if portfolio_item['quantity'] > quantity:
                mongo.db.users.update_one(
                    {'id': session['user_id']},
                    {
                        '$push': {'portfolio': {'stock_id': stock_id, 'quantity': portfolio_item['quantity'] - quantity}}
                    }
                )

            # rejestruje transakcję sprzedaży w bazie danych
            mongo.db.transactions.insert_one({
                'user_id': session['user_id'],
                'stock_id': stock_id,
                'quantity': quantity,
                'price': mongo.db.stocks.find_one({'id': stock_id})['price'],
                'type': 'sell',
                'timestamp': datetime.utcnow()
            })

            # przekierowuje na stronę konta użytkownika
            return redirect(url_for('account'))

    # przekierowuje na stronę konta użytkownika, jeśli niepowodzenie
    return redirect(url_for('account'))

@app.route('/stock_info', methods=['GET'])
def stock_info():
    # sprawdza, czy użytkownik jest zalogowany
    if 'user_id' in session:
        user = mongo.db.users.find_one({'id': session['user_id']})
        stock_id = request.args.get('stock_id')

        # znajduje informacje o akcji w bazie danych
        stock = mongo.db.stocks.find_one({'id': stock_id})
        
        # jeśli akcja istnieje, renderuje stronę z informacjami
        if stock:
            return render_template('stock_info.html', stock=stock, user=user)
        
        # zwraca błąd 404, jeśli akcja nie została znaleziona
        return "Stock not found", 404

    # przekierowuje na stronę główną, jeśli użytkownik nie jest zalogowany
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # usuwa dane sesji użytkownika
    session.pop('user_id', None)

    # przekierowuje na stronę główną
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
