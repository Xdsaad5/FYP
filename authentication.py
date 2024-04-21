from flask import Blueprint, jsonify, request, json, current_app, session
from db_handler import load_firebase_credential
from community import search_user, my_created_community, my_joined_communities
import re
auth_app = Blueprint('authentication', __name__)


def is_valid_email(email):
    # Define a regular expression pattern for a basic email format
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    # Use re.match to check if the email matches the pattern
    match = re.match(email_pattern, email)

    # If there is a match, the email is valid; otherwise, it's not
    return bool(match)


@auth_app.route('/')
def home_page():
    return jsonify(message="Welcome To RouteMate")


@auth_app.route('/api/verification', methods=['POST'])
def verify_new_user():
    signup_info = json.loads(request.data)
    if not is_valid_email(signup_info['email']):
        return jsonify(message="Email format is incorrect.")
    if len(signup_info['password']) < 7:
        return jsonify(message="Password length is too short.")
    status = search_user('email', signup_info['email'])         # check if email already exist or not
    if status > 0:
        return jsonify(message="User with this email is already exist.")
    return signup(signup_info)                                         # if user is verified then we registered his
    # information in firestore


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
        return jsonify(message="True")
    except Exception as e:
        return jsonify(message=str(e))


@auth_app.route('/api/login', methods=['POST'])
def login():
    try:
        user_data = json.loads(request.data)
        if not user_data:
            return jsonify(message="Enter credential required for login.")
        db = load_firebase_credential()
        user_ref = (db.collection(current_app.config.get('USER_COLLECTION')).where('email', '==', user_data['email']).
                    where('password', '==', user_data['password']))
        user_docs = user_ref.get()
        if user_docs:
            temp = [doc.to_dict() for doc in user_docs]
            session['login_email'] = temp[0]['email']
            session['login_name'] = temp[0]['name']
            session['contact'] = temp[0]['contact']
            # after authentication
            my_community = my_created_community()
            joined_community = my_joined_communities()
            data = {
                'created_community': my_community,
                'joined_community': joined_community
            }
            return jsonify(message=data)
        else:
            return jsonify(message="False")
    except Exception as e:
        return jsonify(message=str(e))


@auth_app.route('/api/logout')
def logout():
    try:
        email = session.get('login_email')
        if email is None:
            return jsonify(message="False")
        session.clear()
        return jsonify(message="True")
    except Exception as e:
        print(str(e))
        return jsonify(message="False")
