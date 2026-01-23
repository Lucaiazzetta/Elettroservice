from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

# Connessione a MongoDB locale
client = MongoClient("mongodb://localhost:27017/")
db = client.mio_database
users = db.users

def registra_utente(username, password):
    if users.find_one({"username": username}):
        return {"error": "Utente già esistente"}, 400
    
    hashed_pw = generate_password_hash(password)
    users.insert_one({"username": username, "password": hashed_pw})
    return {"message": "Registrazione completata"}, 201

def verifica_login(username, password):
    user = users.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        return {"message": "Login OK"}, 200
    return {"error": "Credenziali errate"}, 401