from flask import Blueprint, jsonify, request,json,current_app
from db_handler import loadFirebaseCredential

import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
auth_blueprint = Blueprint('authentication', __name__)
otp = 1724
signup_info = {}

def generateOTP():
    global otp
    otp = random.randint(100000, 999999)
    return otp
def sendVerificationEmail(receiver_email):
    server = None
    try:
        sender_email = current_app.config.get('SENDER_EMAIL')
        sender_password = current_app.config.get('EMAIL_PASSWORD')
        subject = current_app.config.get('SUBJECT_EMAIL')
        otp = generateOTP()

        #create the email object(MIME)
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        #attach the body to the email
        message.attach(MIMEText(f"Hey,\nHere is your otp {str(otp)}.\nRegards,\nRouteMate.", 'plain'))

        #establish a connection with the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        server.sendmail(sender_email, receiver_email, message.as_string()) #sending email
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        # Close the connection
        server.quit()


def search_user(field, value,collection_name=None):
    global db
    db = loadFirebaseCredential()
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
def homePage():
    return jsonify(message= "Welcome To RouteMate")
@auth_blueprint.route('/verification',methods=['POST'])
def verifyNewUser():
    signup_info = json.loads(request.data)
    if not is_valid_email(signup_info['email']):
        return jsonify(message="Email format is incorrect.")
    if len(signup_info['password']) < 7:
        return jsonify(message="Password length is too short.")
    status = search_user('email',signup_info['email'])         #check if email already exist or not
    if status > 0:
        return jsonify(message="Email is already exist.")
    status = sendVerificationEmail(signup_info['email'])        #check whether email sent or not also check email is valid or not
    if not status:
        return jsonify(message="Email is not valid.")
    return signup(signup_info)                                         #if user is verified then we registered his information in firestore

@auth_blueprint.route('/storeSignup',methods=['POST'])
def signup(signup_info):
    try:
        db = loadFirebaseCredential()
        if not db:
            return jsonify(message="Error storing user in Firestore.")
        #user is our collection in firestore
        users_ref = db.collection('User')
        #add the user data to Firestore
        user_data = {
            'name': signup_info['name'],
            'email': signup_info['email'],
            'password': signup_info['password'],
            'contact': int(signup_info['contact']),
        }
        #add the document to the 'users' collection
        users_ref.add(user_data)
        return jsonify(message="User successfully stored in Firestore")
    except Exception as e:
        return jsonify(Error=str(e))


@auth_blueprint.route('/login', methods=['POST'])
def login():
    try:
        user_data = json.loads(request.data)
        if not user_data:
            return jsonify(Error="Enter credential required for login.")
        db = loadFirebaseCredential()
        user_ref = (db.collection(current_app.config.get('USER_COLLECTION')).where('email', '==', user_data['email']).
                    where('password', '==', user_data['password']).limit(1))
        user_docs = user_ref.get()
        if len(user_docs) == 1:
            return jsonify(true="True")
        else:
            return jsonify(status="False")
    except Exception as e:
        return jsonify(Error=str(e))
