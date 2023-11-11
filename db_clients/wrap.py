from .db_clients_balance import DB_Client

def welcome_client(Tel_id, username):
    db = DB_Client()
    db.welcome_client(Tel_id, username)
    del db

def get_balance(Tel_id):
    db = DB_Client()
    balance = db.get_balance(Tel_id)
    del db
    return balance

def get_key_wallet(Tel_id):
    db = DB_Client()
    wallet = db.get_wallet(Tel_id)
    del db
    return wallet
