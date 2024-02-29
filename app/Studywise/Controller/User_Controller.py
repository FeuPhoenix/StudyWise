import datetime
from firebase_admin import firestore,auth
from app.Studywise.Model.User_Repo import UserRepo
from Constants import Constants
from Constants.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName 
from flask import request,jsonify,render_template
from firebase_admin import auth

class UserController:
    def __init__(self,user:UserRepo):
        self._firestore = firestore.client()
        self.userList = []
        self.db = FirestoreDB.get_instance()
        self.user=user

    def add_user_to_auth(self, email, password):
        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            print('Successfully created new user:', user.uid)
            #return user
        except Exception as e:
            print('Error creating new user:', e)
            #return None

    async def add_user_to_firestore(self, user_id, user_info):
        try:
            # Check if the user already exists in Firestore
            doc_ref = self.db.collection('Users').document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                print(f'User with ID {user_id} already exists in Firestore.')
                return False, 'User already exists in Firestore.'

            # Check if the user already exists in Firebase Authentication
            try:
                user_record = auth.get_user_by_email(user_info['Email'])
                if user_record:
                    print(f'User with email {user_info["Email"]} already exists in Firebase Authentication.')
                    return False, 'User already exists in Firebase Authentication.'
            except auth.AuthError:
                # This means the user does not exist in Firebase Authentication
                pass

            # User does not exist in Firestore and Firebase Authentication, proceed to add
            await doc_ref.set({
                "Full Name": user_info['Full Name'],
                "Joined on": datetime.now().strftime("%d-%B-%Y"),
                "Email": user_info['Email'],
                "Role": user_info.get("Role", "User"),
                "User_Level": user_info.get("User_Level", 0)
            })
            self.add_user_to_auth(user_info['Email'], user_info['Password'])
            return True, 'User added successfully.'
        except Exception as e:
            print(e)
            return False, str(e)

    async def DeleteUserToFirestore(self, UserID):
        try:
            kUserId = UserID
            await self.db.collection('Users').document(kUserId).delete()
        except Exception as e:
            print(e)
   

    