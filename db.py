import firebase_admin
from firebase_admin import credentials, firestore

def market_collection():
    # credit to video resource https://www.youtube.com/watch?v=qsFYq_1BQdk
    cred = credentials.Certificate("many-markets-db-firebase-adminsdk-fbsvc-24a5086e09.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db