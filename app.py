from flask import Flask
from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy
from community import community_app
from authentication import auth_app
from ride_management import ride_app
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load configuration from config.py
app.config.from_object('config')

# Initialize the session extension
Session(app)

app.register_blueprint(community_app)
app.register_blueprint(auth_app)
app.register_blueprint(ride_app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
