import json,random
from flask import Flask,jsonify,request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.config.from_object('config')
otp = 1724
signup_info = {}
db = None

def loadFirebaseCredential():
    try:
        #Load Firebase credentials from a separate JSON file
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
def generateOTP():
    global otp
    otp = random.randint(100000, 999999)
    return otp
def sendVarificationEmail(receiver_email):
    try:
        sender_email = app.config.get('SENDER_EMAIL')
        sender_password = app.config.get('EMAIL_PASSWORD')
        subject = app.config.get('SUBJECT_EMAIL')
        otp = generateOTP()

        #create the email object(MIME)
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        #attach the body to the email
        message.attach(MIMEText(str(otp), 'plain'))

        #establish a connection with the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        server.sendmail(sender_email, receiver_email, message.as_string()) #sending email

        print("Email has been sent to " + receiver_email)
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        # Close the connection
        server.quit()


def search_user(field, value,collection_name='User'):
    global db
    if not db:
        db = loadFirebaseCredential()
    query = db.collection(collection_name).where(field, '==', value).limit(1)
    result = query.get()

    # Check if there is at least one document matching the condition
    return len(result)

@app.route('/')
def homePage():
    return jsonify(message= "Welcome To RouteMate")
@app.route('/verification',methods=['POST'])
def verifyNewUser():
    #ignup_info = json.loads(request.data)
    ''' for my testing
    signup_info = jsonify(name="ahsan", email='bsef20a010@pucit.edu.pk', password="ahsan", contact=92289382)
    data = signup_info.get_json()'''
    status = search_user('email',signup_info['email'])         #check if email already exist or not
    print(f"status = {status}")
    if status > 0:
        return jsonify(message="Email is already exist.")
    status = sendVarificationEmail(signup_info['email'])        #check whether email sent or not also check email is valid or not
    print(f"status {status}")
    if not status:
        return jsonify(message="Email is not valid.")
    return jsonify(message="true")
@app.route('/storeSignup',methods=['POST'])
def signup():
    signup_info = json.loads(request.data)
    '''
    for my testing 
    signup_info= jsonify(name="ahsan",email='bsef20a010@pucit.edu.pk',password="ahsan",contact=92289382)
    data = signup_info.get_json()'''
    global db
    if not db:
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
app.run()

