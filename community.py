import json
from flask import Blueprint, jsonify, request, current_app, session
from authentication import search_user
from db_handler import load_firebase_credential
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
community_blueprint = Blueprint('community', __name__)
otp = 0000


def generate_otp():
    global otp
    otp = random.randint(1000, 9999)
    return otp


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


def already_exist_community(community_info):                            # this function checks if community  exist already or not
    if not community_info:                                              # check if community(object) is null
        return jsonify(message="Provided Community information isn't completed.")
    status = search_user('name', community_info['name'], current_app.config.get('COMMUNITY_COLLECTION'))              # check whether community already exist or not?
    if status > 0:
        return jsonify(message="Community already exist.")
    return True


''' if user enter email then am sending him verification email and store user data 
in his session so that if he verified then I can enter his community in my db'''


def storing_community_information_in_session(comm_info):
    try:
        session['name'] = comm_info['name']
        session['description'] = comm_info['description']
        session['email'] = comm_info['email']
        if comm_info['code']:
            session['code'] = comm_info['code']
        else:
            session['code'] = None
    except Exception as e:
        return jsonify(message=str(e))


@community_blueprint.route('/api/create/community/by/code', methods=['POST'])
def create_community_by_code():
    try:
        com_info = json.loads(request.data)
        status = already_exist_community(com_info)
        if str(status) != "True":
            return status
        print(status)
        db = load_firebase_credential()
        if not db:
            return jsonify(message="Error in creating community.")
        # community is our collection in firestore
        comm_ref = db.collection(current_app.config.get('COMMUNITY_COLLECTION'))
        # add the community data to Firestore
        community_data = {
            'name': com_info['name'],
            'description': com_info['description'],
            'code': com_info['code'],
            'email': None
        }
        # add the document to the 'community' collection
        comm_ref.add(community_data)
        return jsonify(message="True")
    except Exception as e:
        return jsonify(message=str(e))


@community_blueprint.route('/api/verified/community')
def storing_verified_community():
    try:
        db = load_firebase_credential()
        if not db:
            return jsonify(message="Error in creating community.")
        # community is our collection in firestore
        comm_ref = db.collection(current_app.config.get('COMMUNITY_COLLECTION'))
        # add the community data to Firestore
        community_data = {
            'name': session.get('name'),
            'description': session.get('description'),
            'code': session.get('code'),
            'email': session.get('email')
        }
        # add the document to the 'community' collection
        comm_ref.add(community_data)
        return jsonify(message="True")
    except Exception as e:
        return jsonify(message=str(e))


@community_blueprint.route('/api/getotp', methods=['POST'])
def otp_for_community_creation():
    community_info = json.loads(request.data)
    status = already_exist_community(community_info)
    if str(status) != 'True':
        return status
    # send user otp
    send_verification_email(community_info['email'])
    storing_community_information_in_session(community_info)
    global otp
    return jsonify(message=str(otp))


@community_blueprint.route('/api/search/community', methods=['POST'])
def search_community():
    try:
        search_com = json.loads(request.data)
        if not search_com:  # check if search(object) is null
            return jsonify(message="Nothing Found")
        db = load_firebase_credential()
        collection_name = current_app.config.get('COMMUNITY_COLLECTION')
        query = db.collection(collection_name).order_by('name')     # getting all the records from the database
        result = query.get()
        result_list=[]
        for doc in result:
            doc_data = doc.to_dict()
            if  search_com['name'] in doc_data['name']:
                result_list.append(doc_data)
        print(result_list)
        return jsonify(message=result_list)
        # Check if there is at least one document matching the condition
    except Exception as e:
        print(str(e))
        return jsonify(message=str(e))
