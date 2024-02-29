from flask import Flask
from firebase_admin import credentials, initialize_app
cred = credentials.Certificate("firebasetest/key.json")
default_app=initialize_app(cred)
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    from ..app.Studywise.userAPI import userAPI
    app.register_blueprint(userAPI,url_prefix='/user')
    return app