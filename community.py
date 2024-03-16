import json
from flask import Blueprint, jsonify, request, current_app, session
from db_handler import load_firebase_credential
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
community_app = Blueprint('community', __name__)
otp = 0000


def generate_otp():
    global otp
    otp = random.randint(1000, 9999)
    return otp


def search_user(field, value, collection_name=None):
    db = load_firebase_credential()
    collection_name = collection_name or current_app.config.get('USER_COLLECTION')
    query = db.collection(collection_name).where(field, '==', value).limit(1)
    result = query.get()

    # Check if there is at least one document matching the condition
    return len(result)


def search_community_by_code(code, name):
    try:
        if not code:
            return False
        db = load_firebase_credential()
        collection_name = current_app.config.get('COMMUNITY_COLLECTION')
        query = db.collection(collection_name).where('code', '==', code).where('name', '==', name)
        result = query.get()
        result = [doc.to_dict() for doc in result]
        if not result:
            return False
        return result
    except Exception as e:
        print(str(e))
        return False


def send_verification_email(receiver_email):
    server = None
    try:
        sender_email = current_app.config.get('SENDER_EMAIL')
        sender_password = current_app.config.get('EMAIL_PASSWORD')
        subject = current_app.config.get('SUBJECT_EMAIL')
        global otp
        otp = generate_otp()

        # create the email object(MIME)
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        # attach the body to the email
        message.attach(MIMEText(f"Hey,\nHere is your otp {str(otp)}.\nRegards,\nRouteMate.", 'plain'))

        # establish a connection with the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        server.sendmail(sender_email, receiver_email, message.as_string())      # sending email
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        # Close the connection
        server.quit()


# this function checks if community  exist already or not


def already_exist_community(community_info):
    # check if community(object) is null
    if not community_info:
        return jsonify(message="Provided Community information isn't completed.")
    # check whether community already exist or not?
    status = search_user('name', community_info['name'], current_app.config.get('COMMUNITY_COLLECTION'))
    if status > 0:
        return jsonify(message="Community already exist.")
    return True


''' if user enter email then am sending him verification email and store user data 
in his session so that if he verified then I can enter his community in my db'''


def storing_community_information_in_session(comm_info):
    try:
        if comm_info['code']:
            session['code'] = comm_info['code']
        else:
            session['code'] = None
        session['created_community_name'] = comm_info['name']
        session['created_community_description'] = comm_info['description']
        session['created_community_domain'] = comm_info['domain']
        session['owner_email'] = session.get('login_email')
    except Exception as e:
        return jsonify(message=str(e))


''' this function will create community on the basis of user provided code and also store its email by getting it from 
 session so that we can get all the community created by him'''


@community_app.route('/api/create/community/by/code', methods=['POST'])
def create_community_by_code():
    try:
        com_info = json.loads(request.data)
        status = already_exist_community(com_info)
        if str(status) != "True":
            return status
        db = load_firebase_credential()
        # community is our collection in firestore
        comm_ref = db.collection(current_app.config.get('COMMUNITY_COLLECTION'))
        domain = None                       # it is just for help if domain doesn't come then we use this
        if com_info['domain']:
            domain = com_info['domain']
        # add the community data to Firestore
        community_data = {
            'name': com_info['name'],
            'description': com_info['description'],
            'code': com_info['code'],
            'owner_email': session.get('login_email'),
            'domain': domain
        }
        print(community_data)
        # add the document to the 'community' collection
        comm_ref.add(community_data)
        # add the document to the 'JOIN_COMMUNITIES' collection
        comm_ref = db.collection(current_app.config.get('JOIN_COMMUNITIES_COLLECTION'))
        data = {
            'community_name': com_info['name'],
            'email': session.get('login_email')
        }
        comm_ref.add(data)
        return jsonify(message="True")
    except Exception as e:
        return jsonify(message=str(e))


# this function will store user created community in db after verification of otp

@community_app.route('/api/verified/community')
def storing_verified_community():
    try:
        db = load_firebase_credential()
        if not db:
            return jsonify(message="Error in creating community.")
        # community is our collection in firestore
        comm_ref = db.collection(current_app.config.get('COMMUNITY_COLLECTION'))
        # add the community data to Firestore
        community_data = {
            'name': session.get('created_community_name'),
            'description': session.get('created_community_description'),
            'code': session.get('code'),
            'owner_email': session.get('owner_email'),
            'domain': session.get('created_community_domain')
        }
        # add the document to the 'community' collection
        comm_ref.add(community_data)
        comm_ref = db.collection(current_app.config.get('JOIN_COMMUNITIES_COLLECTION'))
        data = {
            'community_name': session.get('created_community_name'),
            'email': session.get('login_email')
        }
        comm_ref.add(data)
        return jsonify(message="True")
    except Exception as e:
        return jsonify(message=str(e))


# this function will verify whether a person has valid email-domain or not
@community_app.route('/api/getotp', methods=['POST'])
def otp_for_community_creation():
    community_info = json.loads(request.data)
    status = already_exist_community(community_info)
    if str(status) != 'True':
        return status
    # send user otp
    send_verification_email(community_info['domain'])
    storing_community_information_in_session(community_info)
    global otp
    return jsonify(message=str(otp))

# we are not using this function


@community_app.route('/api/search/community', methods=['POST'])
def search_community():
    try:
        search_com = json.loads(request.data)
        if not search_com:  # check if search(object) is null
            return jsonify(message="Nothing Found")
        db = load_firebase_credential()
        collection_name = current_app.config.get('COMMUNITY_COLLECTION')
        query = db.collection(collection_name).order_by('name')     # getting all the records from the database
        result = query.get()
        result_list = []
        for doc in result:
            doc_data = doc.to_dict()
            if search_com['name'].lower() in doc_data['name'].lower():
                result_list.append(doc_data)
        return jsonify(message=result_list)
        # Check if there is at least one document matching the condition
    except Exception as e:
        print(str(e))
        return jsonify(message=str(e))


# this function will return the communities which one user made itself

@community_app.route('/api/my/created/community')
def my_created_community():
    try:
        email = session.get('login_email')
        if email is None:
            return jsonify(message="False")
        db = load_firebase_credential()
        collection_name = current_app.config.get('COMMUNITY_COLLECTION')
        query = db.collection(collection_name).where('owner_email', '==', email)
        result = query.get()
        result_list = []
        for doc in result:
            doc_data = doc.to_dict()
            temp = {
                "name": doc_data['name']
            }
            result_list.append(temp)
        return result_list
    except Exception as e:
        print(str(e))
        return jsonify(message="False")


@community_app.route('/api/my/joined/community')
def my_joined_communities():
    try:
        email = session.get('login_email')
        if email is None:
            return jsonify(message="False")
        db = load_firebase_credential()
        collection_name = current_app.config.get('JOIN_COMMUNITIES_COLLECTION')
        query = db.collection(collection_name).where('email', '==', email)
        result = query.get()
        result_list = []
        for doc in result:
            doc_data = doc.to_dict()
            temp = {
                "name": doc_data['community_name']
            }
            result_list.append(temp)
        return result_list
    except Exception as e:
        print(str(e))
        return jsonify(message="False")


# get all community

@community_app.route('/api/get/all/community')
def all_community():
    try:
        db = load_firebase_credential()
        collection_name = current_app.config.get('COMMUNITY_COLLECTION')
        query = db.collection(collection_name)
        result = query.get()
        result_list = []
        for doc in result:
            doc_data = doc.to_dict()
            result_list.append(doc_data)
        print(result_list)
        return jsonify(message=result_list)
    except Exception as e:
        print(str(e))
        return jsonify(message="No Community Exist.")


def already_joined_in_community(name, email):
    try:
        db = load_firebase_credential()
        collection_name = current_app.config.get('JOIN_COMMUNITIES_COLLECTION')
        query = db.collection(collection_name).where('email', '==', email).where('community_name', '==', name).limit(1)
        result = query.get()
        if len(result) == 0:
            return True
        return False
    except Exception as e:
        print(str(e))

# get all the members of the community and add him in that community


@community_app.route('/api/join/community', methods=['POST'])
def join_community():
    try:
        com_name = json.loads(request.data)
        status = already_joined_in_community(com_name['name'], session.get('login_email'))
        if not status:
            return jsonify(message=False)
        db = load_firebase_credential()
        collection_name = current_app.config.get('JOIN_COMMUNITIES_COLLECTION')
        ref = db.collection(collection_name)
        data = {
            'email': session.get('login_email'),
            'community_name': com_name['name']
        }
        ref.add(data)
        return get_all_members(com_name['name'])
    except Exception as e:
        print(str(e))
        return jsonify(message="False")


# get all members of the community:


@community_app.route('/api/get/all/members', methods=['POST'])
def get_all_members(com_name=None):
    try:
        if not com_name:
            temp = json.loads(request.data)
            com_name = temp['name']
        db = load_firebase_credential()
        collection_name = current_app.config.get('JOIN_COMMUNITIES_COLLECTION')
        query = db.collection(collection_name).where('community_name', '==', com_name)
        result = query.get()
        result_list = []
        for doc in result:
            doc_data = doc.to_dict()
            temp = {
                "name": doc_data['email'].split('@')[0]
            }
            result_list.append(temp)
        return jsonify(message=result_list)
    except Exception as e:
        print(str(e))
        return jsonify(message=False)
