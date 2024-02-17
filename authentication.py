from flask import Blueprint, jsonify, request, json, current_app
from db_handler import load_firebase_credential

import re

auth_blueprint = Blueprint('authentication', __name__)


def search_user(field, value, collection_name=None):
    db = load_firebase_credential()
    collection_name = collection_name or current_app.config.get('USER_COLLECTION')
    query = db.collection(collection_name).where(field, '==', value).limit(1)
    result = query.get()

    # Check if there is at least one document matching the condition
    return len(result)


def is_valid_email(email):
    # Define a regular expression pattern for a basic email format
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    # Use re.match to check if the email matches the pattern
    match = re.match(email_pattern, email)

    # If there is a match, the email is valid; otherwise, it's not
    return bool(match)


@auth_blueprint.route('/')
def home_page():
    return jsonify(message="Welcome To RouteMate")


@auth_blueprint.route('/api/verification', methods=['POST'])
def verify_new_user():
    signup_info = json.loads(request.data)
    if not is_valid_email(signup_info['email']):
        return jsonify(message="Email format is incorrect.")
    if len(signup_info['password']) < 7:
        return jsonify(message="Password length is too short.")
    status = search_user('email', signup_info['email'])         # check if email already exist or not
    if status > 0:
        return jsonify(message="User with this email is already exist.")
    return signup(signup_info)                                         # if user is verified then we registered his information in firestore


@auth_blueprint.route('/api/storeSignup', methods=['POST'])
def signup(signup_info):
    try:
        db = load_firebase_credential()
        if not db:
            return jsonify(message="Error storing user in Firestore.")
        # user is our collection in firestore
        users_ref = db.collection('User')
        # add the user data to Firestore
        user_data = {
            'name': signup_info['name'],
            'email': signup_info['email'],
            'password': signup_info['password'],
            'contact': int(signup_info['contact']),
        }
        # add the document to the 'users' collection
        users_ref.add(user_data)
        return jsonify(message="User successfully stored in Firestore")
    except Exception as e:
        return jsonify(message=str(e))


@auth_blueprint.route('/api/login', methods=['POST'])
def login():
    try:
        user_data = json.loads(request.data)
        if not user_data:
            return jsonify(message="Enter credential required for login.")
        db = load_firebase_credential()
        user_ref = (db.collection(current_app.config.get('USER_COLLECTION')).where('email', '==', user_data['email']).
                    where('password', '==', user_data['password']).limit(1))
        user_docs = user_ref.get()
        if len(user_docs) == 1:
            return jsonify(message="True")
        else:
            return jsonify(message="False")
    except Exception as e:
        return jsonify(message=str(e))
