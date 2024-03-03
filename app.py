from flask import Flask
from community import community_blueprint
from authentication import auth_blueprint
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.config.from_object('config')

app.register_blueprint(community_blueprint)

app.register_blueprint(auth_blueprint)
app.run()
