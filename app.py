import json

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config.from_object('config')


from community import community_blueprint
app.register_blueprint(community_blueprint)
from authentication import auth_blueprint
app.register_blueprint(auth_blueprint)
app.run()

