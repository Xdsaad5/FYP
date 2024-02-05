import firebase_admin
from firebase_admin import credentials, firestore
import json
db = None
def loadFirebaseCredential():
    try:
        global db
        if  db:
            return db
        #Load Firebase credentials from a routemate_private_key JSON file
        credentials_path = 'routemate_private_key.json'
        with open(credentials_path, 'r') as file:
            firebase_credentials = json.load(file)
        # Initialize Firebase
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)
        # Create a Firestore client
        db = firestore.client()
        return db
    except Exception as e:
        return None