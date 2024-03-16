from flask import Flask
from community import community_app
from authentication import auth_app
from ride_management import ride_app
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.config.from_object('config')

app.register_blueprint(community_app)

app.register_blueprint(auth_app)

app.register_blueprint(ride_app)

app.run()
