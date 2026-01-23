from flask import Flask, request, jsonify, session
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chiave_fissa_per_non_perdere_sessioni" # Non cambiarla

# Configurazione CORS per gestire i cookie (fondamentale per errore 401)
CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5500", "http://localhost:5500"])

# Connessione MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['mio_database']
users_col = db['users']
quotes_col = db['quotes']

@app.route('/api/register', methods=['POST'])
def handle_register():
    data = request.json
    if users_col.find_one({"username": data.get('username')}):
        return jsonify({"success": False, "message": "Utente già esistente"}), 400
    hashed_pw = generate_password_hash(data.get('password'))
    users_col.insert_one({"username": data.get('username'), "password_hash": hashed_pw, "role": "user"})
    return jsonify({"success": True, "message": "Registrato!"}), 201

@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.json
    user = users_col.find_one({"username": data.get('username')})
    if user and check_password_hash(user['password_hash'], data.get('password')):
        session.clear() 
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        session['role'] = user.get('role', 'user')
        return jsonify({"success": True, "redirect": "dashboard-client.html" if user.get('role') == "user" else "dashboard-admin.html"}), 200
    return jsonify({"success": False, "message": "Credenziali errate"}), 401

@app.route('/api/submit_quote', methods=['POST'])
def handle_submit_quote():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Sessione non valida. Rifai il login"}), 401
    data = request.json
    quotes_col.insert_one({
        "user_id": session['user_id'],
        "username": session['username'],
        "title": data.get('title'),
        "description": data.get('description'),
        "date": datetime.now().strftime("%d/%m/%Y")
    })
    return jsonify({"success": True, "message": "Preventivo inviato con successo!"}), 201

@app.route('/api/get_quotes', methods=['GET'])
def handle_get_quotes():
    if 'user_id' not in session:
        return jsonify({"success": False}), 401
    query = {} if session.get('role') == 'admin' else {"user_id": session['user_id']}
    quotes = list(quotes_col.find(query))
    for q in quotes: q['_id'] = str(q['_id'])
    return jsonify(quotes), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)