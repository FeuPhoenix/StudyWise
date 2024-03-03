from flask import Flask
from firebase_admin import credentials, initialize_app
from app.Studywise.Model.User_Controller import UserController  # Ensure this path is correct

# Initialize Firebase Admin
cred = credentials.Certificate("Studywise/key.json")
default_app = initialize_app(cred, {
    'storageBucket': 'gs://studywise-dba07.appspot.com'
})

# Create Flask application
def create_app():
    studywise = Flask(__name__)  # Use lowercase for the Flask app instance
    studywise.config['SECRET_KEY'] = 'secret!'

    # Register routes
    @studywise.route('/create_user', methods=['POST'])
    def create_user():
        return UserController.create_user()

    @studywise.route('/get_user/<user_id>', methods=['GET'])
    def get_user(user_id):
        return UserController.get_user_info(user_id)  # Ensure this method name matches the one in UserController

    @studywise.route('/delete_user/<user_id>', methods=['DELETE'])
    def delete_user(user_id):
        return UserController.delete_user_info(user_id)  # Ensure this method name matches the one in UserController

    # Register userAPI Blueprint if it exists and is set up correctly
    # from Studywise.userAPI import userAPI  # Uncomment and ensure this import path is correct
    # studywise.register_blueprint(userAPI, url_prefix='/user')  # Uncomment if you're using a Blueprint

    return studywise

# Instantiate the Flask application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
