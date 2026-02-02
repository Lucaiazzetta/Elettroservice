from flask import Flask, request, jsonify, session
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId # Importante: serve per gestire gli ID di MongoDB

app = Flask(__name__)
# La secret_key DEVE essere una stringa fissa per mantenere i cookie attivi
app.secret_key = "una_stringa_molto_segreta_e_fissa" 

# Configurazione CORS aggiornata per Jan 2026
CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5500", "http://localhost:5500"])

client = MongoClient("mongodb://localhost:27017/")
db = client['mio_database']
users_col = db['users']
quotes_col = db['quotes']

@app.route('/api/register', methods=['POST'])
def route_register():
    data = request.json
    if users_col.find_one({"username": data.get('username')}):
        return jsonify({"success": False, "message": "Utente già esistente"}), 400
    hashed_pw = generate_password_hash(data.get('password'))
    users_col.insert_one({"username": data.get('username'), "password_hash": hashed_pw, "role": "user"})
    return jsonify({"success": True, "message": "Registrato!"}), 201

@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.json
    
    # 1. Cerca l'utente
    user = users_col.find_one({"username": data.get('username')})

    # 2. Verifica password
    if user and check_password_hash(user['password_hash'], data.get('password')):
        
       
        session['user_id'] = str(user['_id'])
        session['role'] = user.get("role", "user")
        session['username'] = user["username"]
       

        return jsonify({
            "success": True, 
            "message": "Login effettuato!",
            "role": session['role'], 
            "username": session['username']
        }), 200
    
    return jsonify({"success": False, "message": "Credenziali non valide"}), 401


@app.route('/api/submit_quote', methods=['POST'])
def route_submit():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Sessione non valida"}), 401
    data = request.json
    quotes_col.insert_one({
        "user_id": session['user_id'],
        "username": session['username'],
        "title": data.get('title'),
        "description": data.get('description'),
        "date": datetime.now().strftime("%d/%m/%Y")
    })
    return jsonify({"success": True, "message": "Inviato!"}), 201

@app.route('/api/get_quotes', methods=['GET'])
def route_get():
    if 'user_id' not in session:
        return jsonify({"success": False}), 401
    query = {} if session.get('role') == 'admin' else {"user_id": session['user_id']}
    quotes = list(quotes_col.find(query))
    for q in quotes: q['_id'] = str(q['_id'])
    return jsonify(quotes), 200

@app.route('/api/get_quotes', methods=['GET'])
def call_get_quotes():
    if 'user_id' not in session:
        return jsonify({"success": False}), 401
    
    query = {} if session.get('role') == 'admin' else {"user_id": session['user_id']}
    quotes = list(quotes_col.find(query))
    
    for q in quotes: 
        q['_id'] = str(q['_id'])
        # Flask invierà tutto: title, description, status, price, ecc.
    return jsonify(quotes), 200

@app.route('/api/update_quote', methods=['POST'])
def call_update_quote():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Non autorizzato"}), 403

    data = request.json
    try:
        quotes_col.update_one(
            {"_id": ObjectId(data.get('id'))}, # Converte l'ID
            {"$set": {
                "status": data.get('status'),
                "price": data.get('price'),
                "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M")
            }}
        )
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    

if __name__ == '__main__':
    # Controlla se esiste almeno un utente con ruolo 'admin'
    if users_col.count_documents({"role": "admin"}) == 0:
        print("🛠️ Nessun amministratore trovato. Creazione admin di default...")
        
        admin_data = {
            "username": "admin",
            "password_hash": generate_password_hash("admin123"), 
            "role": "admin"
        }
        users_col.insert_one(admin_data)
        print("✅ Admin creato con successo! User: admin | Pass: admin123")
    else:
        print("👋 Admin già presente nel database.")

    app.run(host='127.0.0.1', port=5000, debug=True)