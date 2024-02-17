
from flask import Flask
from community import community_blueprint
from authentication import auth_blueprint
app = Flask(__name__)
app.config.from_object('config')

app.register_blueprint(community_blueprint)

app.register_blueprint(auth_blueprint)
app.run()
