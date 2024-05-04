from datetime import datetime
import uuid
from firebase_admin import firestore, auth

from FirestoreDB import FirestoreDB
from Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName 
from flask import request,jsonify,render_template
from FirestoreDB import FirestoreDB
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
            # Get the data of the document
            user_data = doc.to_dict()
            
            # Print the data of the document
            print("User data retrieved from Firestore:")
            print(user_data)

            # Return the data of the document
            return user_data

        # If no document is found for the user's email
        print(f"No document found for user with email {self.email} in Firestore.")
        return None


        
    @classmethod
    def fromJson(cls, data):
        return cls(
            email=data["Email"],
            fName=data["Full Name"],
            dateJoined=data["Joined on"],
            password=data["Password"],
            Role=data["Role"],
            User_Level=data[0],
            
        )

    def toJson(self):
        data = {
            "Full Name": self.fullName,
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

                    # Get a reference to the document
                    doc_ref = users_ref.document(doc_id)
                    now=datetime.now()
                    # Update a field (e.g., 'last_login_time') before returning
                    doc_ref.update({'last_login_time':f'{now.strftime("%m/%d/%Y, %H:%M:%S")}'})
                    
                    # Return the document ID and True
                    return doc_id, True
            else:
            # If no document is found for the user's email and password
                return None, False
    def add_user_to_firestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        # Check if the user already exists in Firestore using email
        users_ref = firestore_instance.collection('Users')
        query = users_ref.where('Email', '==', self.email)
        docs = query.stream()

        for doc in docs:
            print(f"Document with email {self.email} already exists in Firestore.")
            return None  # Return None if the email already exists

        # If the email doesn't exist in Firestore, proceed to add the user
        try:
            # Check if the user exists in authentication
            user = auth.get_user_by_email(self.email)
            print(f"User with email {self.email} already exists in Authentication.")
        except auth.UserNotFoundError:
            # User doesn't exist in authentication, proceed to add to Firestore and authentication
            # Add user to authentication
            user = auth.create_user(email=self.email, password=self.password)
            print(f"User added to Authentication with ID: {user.uid}")
            
            # Add user to Firestore
            doc_ref = users_ref.document(user.uid)
            doc_ref.set(self.toJson())
            print(f"User added to Firestore with email: {self.email}")




    
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
#Testing
def main():
    print(UserRepo.Login("a123451@.com","123456"))
    a=UserRepo("a1234@gmail.com","Mohamed Abdallah","123456")
    a.add_user_to_firestore()
    z,b=UserRepo.Login("a1234@gmail.com","123456")
    # print(z,b)
    
if __name__ == '__main__':
     main()
     