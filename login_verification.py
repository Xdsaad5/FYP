import firebase_admin
from firebase_admin import credentials, auth
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import  request, Flask

app = Flask(__name__)
def send_email(data):
    # Create the email message
    message = MIMEMultipart()
    message['From'] = data['sender_email']
    message['To'] = data['recipient_email']
    message['Subject'] = data['subject']

    # Attach the email body
    message.attach(MIMEText(data['body'], 'plain'))

    # Connect to the SMTP server (in this case, Gmail's SMTP server)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Use TLS for security
        server.login('xdsaad5@gmail.com', data['password'])
        server.sendmail(data['sender_email'], data['recipient_email'], message.as_string())
email = 'saad17mughal@gmail.com'
password="okdopjce"
#email = input("Enter your email: ")
#password = input("Enter your password: ")
cred = credentials.Certificate('routemate_private_key.json')
firebase_admin.initialize_app(cred)
user = auth.create_user(
    email=email,
    password=password,
    email_verified=False
)
print(f"user id: {user.uid}")
# Get the user's ID token
link = auth.generate_email_verification_link(user.email)
print(link)

# Extract oobCode from the link
token = link.split('oobCode=')[1].split('&')[0]

email_content = {"sender_email": 'routemat@gmail.com', 'recipient_email': email,
                 'password':'zanv ofoz mafa ipik' , 'subject': 'Email Verification', 'body': link}

print(email_content)

send_email(email_content)

# Verify the user's email
@app.route('/verify_email', methods=['GET'])
def verify_email():
    print('verify email')
    oob_code = request.args.get('oobCode')
    try:
        # Verify the email using the oobCode
        auth.verify_email_verification_code(oob_code)
        print("Email verification successful.")
    except Exception as e:
        print(f"Error verifying email: {e}")

if __name__ == '__main__':
    app.run(host='localhost', port=5000)



