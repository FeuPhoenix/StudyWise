from datetime import datetime
import uuid
from firebase_admin import firestore, auth

from backend.Classes.FirestoreDB import FirestoreDB
# from FirestoreDB import FirestoreDB

class UserRepo:
    
    def __init__(self,email, fullName,password ,Role=None,User_Level=0,dateJoined=None ):
        self.email = email
        self.fullName = fullName
        self.dateJoined = dateJoined
        self.Role = Role
        self.User_Level=User_Level
        self.userID=uuid.uuid4().hex
        self.password=password
        

    def getUserDataFromFirestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        users_ref = firestore_instance.collection('Users')

        # Query Firestore to find the document with the matching email
        query = users_ref.where('Email', '==', self.email)    
        docs = query.stream()

        for doc in docs:
            # Get the ID of the document
            doc_id = doc.id

            full_name = doc.to_dict().get('full_name')
            if full_name:
                print(f'Logged in: {full_name}')
            else:
                print('full_name field is empty in this document.')

            # Return the document ID, full_name, and True
            return doc_id, full_name, True

        # If no document is found with the given email and password
        return None, None, False


        
    @classmethod
    def fromJson(cls, data):
        return cls(
            email=data["Email"],
            fName=data["full_name"],
            dateJoined=data["Joined on"],
            password=data["Password"],
            Role=data["Role"],
            User_Level=data[0],
            
        )

    def toJson(self):
        data = {
            "full_name": self.fullName,
            "Joined on": datetime.now().strftime("%d-%B-%Y"),
            "Password":self.password,
            "Email": self.email,
            "Role": self.Role,
            "User_Level": 0,
            "last_login_time":"" 
        }
        return data
    
    @staticmethod
    def check_user_exists_in_auth(email):
        try:
            user = auth.get_user_by_email(email)
            print(True)
            return True
        except auth.UserNotFoundError:
            print(False)
            return False
    @staticmethod
    def get_password_by_email(email):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        users_ref = firestore_instance.collection('Users')
        query = users_ref.where('Email', '==', email)
        docs = query.stream()
        for doc in docs:
            return doc.to_dict().get('Password')
        return None

    @staticmethod
    def Login(email, password):
            db_instance = FirestoreDB.get_instance()
            firestore_instance = db_instance.get_firestore_instance()
            users_ref = firestore_instance.collection('Users')
            if UserRepo.check_user_exists_in_auth(email):
                # Query Firestore to find the document with the matching email and password
                query = users_ref.where('Email', '==', email).where('Password', '==', password)    
                docs = query.stream()

                for doc in docs:
                    # Get the ID of the document
                    doc_id = doc.id

                    full_name = doc.to_dict().get('full_name')

                    # Return the document ID, full_name, and True
                    return doc_id, full_name, True

            # If no document is found with the given email and password
            return None, None, False
    # @staticmethod
    # def Login(email, password):
    #     try:
    #         auth_instance = FirestoreDB.get_auth_instance()
    #         # Authenticate user with provided email and password
    #         user = auth_instance.get_user_by_email(email)

    #         # Check if user exists and verify password
    #         if user and auth.verify_password(email, password):
    #             print(f"User logged in: {user.uid}")
    #             db_instance = FirestoreDB.get_instance()
    #             firestore_instance = db_instance.get_firestore_instance()
    #             users_ref = firestore_instance.collection('Users')
                
    #                 # Query Firestore to find the document with the matching email and password
    #             query = users_ref.where('Email', '==', email).where('Password', '==', password)    
    #             docs = query.stream()

    #             for doc in docs:
    #                 # Get the ID of the document
    #                 doc_id = doc.id

    #                 full_name = doc.to_dict().get('full_name')

    #                 # Return the document ID, full_name, and True
    #                 return doc_id, full_name, True
    #         else:
    #             print("Invalid credentials")
    #             return None

    #     except Exception as e:
    #         print(f"Error logging in: {e}")
    #         return None
    def add_user_to_firestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        # Check if the user already exists in Firestore using email
        users_ref = firestore_instance.collection('Users')
        query = users_ref.where('Email', '==', self.email)
        docs = query.stream()

        for doc in docs:
            print(f"User with email {self.email} already exists in Firestore.")
            return None  # Return None if the email already exists

        # If the email doesn't exist in Firestore, proceed to add the user
        try:
            # Check if the user exists in authentication
            user = auth.get_user_by_email(self.email)
            print(f"User with email {self.email} already exists in Authentication.")
            return None
        except auth.UserNotFoundError: # User doesn't exist in authentication, proceed to add to Firestore and authentication
            import time
            # Add user to authentication
            user = auth.create_user(email=self.email, password=self.password)
            print(f"User added to Authentication with ID: {user.uid}")
            
            # Add user to Firestore
            doc_ref = users_ref.document(user.uid)
            doc_ref.set(self.toJson())
            time.sleep(1) # Give the User Creation a chance to execute
            print(f"User added to Firestore with email: {self.email}")
            return True

    @staticmethod
    def update_user_name_by_id(doc_id, new_name):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        users_ref = firestore_instance.collection('Users')

        try:
            # Retrieve the document with the matching document ID
            doc_ref = users_ref.document(doc_id)
            doc = doc_ref.get()

            if doc.exists:
                # Get the current full_name
                current_full_name = doc.to_dict().get('full_name')

                if current_full_name:
                    print(f'Current full_name: {current_full_name}')
                else:
                    print('full_name field is empty in this document.')

                # Update the document with the new full_name
                new_name = str(new_name)  # Ensure new_name is a string
                doc_ref.update({'full_name': new_name})
                print(f'Updated full_name to: {new_name}')

                return True
            else:
                print(f'No document found with ID: {doc_id}')
                return False

        except Exception as e:
            print(f'Error updating name for document ID {doc_id}: {e}')
            return False

    @staticmethod
    def update_user_name_by_email(email, new_name):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        users_ref = firestore_instance.collection('Users')

        # Query Firestore to find the document with the matching email
        query = users_ref.where('Email', '==', email)
        docs = query.stream()

        for doc in docs:
            # Get the ID of the document
            doc_id = doc.id

            full_name = doc.to_dict().get('full_name')
            if full_name:
                print(f'Logged in: {full_name}')
            else:
                print('full_name field is empty in this document.')

            # Update the document with the new full_name
            users_ref.document(doc_id).update({'full_name': new_name})
            print(f'Updated full_name to: {new_name}')

            # Return the document ID, new full_name, and True
            return doc_id, new_name, True

    # If no document is found with the given email
        return None, None, False
    
    @staticmethod
    def getUser_level_from_Firestore(ID):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        user_doc_ref = firestore_instance.collection('Users').document(ID)

        # Get the document snapshot
        doc_snapshot = user_doc_ref.get()

        # Check if the document exists
        if doc_snapshot.exists:
            # Get the data of the document
            user_data = doc_snapshot.to_dict()
            
            # Get the value of the User_Level field
            user_level = user_data.get('User_Level')

            # Print the data of the document
            print("User data retrieved from Firestore:")
            print(user_data)

            # Return the User_Level value
            return user_level
        else:
            # If no document is found for the user's ID
            print(f"No document found for user with ID {ID} in Firestore.")
            return None
     