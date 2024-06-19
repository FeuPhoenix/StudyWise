import sys
from firebase_admin import firestore,auth
from firebase_admin import auth
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii

from FirestoreDB import FirestoreDB
from User_Repo import UserRepo
sys.path.append('D:/COLLEGE/StudyWise/app/StudyWise')

class UserController:
    @staticmethod
    def deleteUser(id,email):
        # Delete from Firestore
        UserController.deleteFromFirestore(id)
        
        # Delete from Authentication
        UserController.deleteFromAuthentication(email,id)
    @staticmethod
    def deleteFromAuthentication(email):
        try:
            # Delete the user from authentication
            user = auth.get_user_by_email(email)
            auth.delete_user(id)
            print(f"User with email {email} deleted from Authentication.")
        except auth.UserNotFoundError:
            print(f"User with email {email} not found in Authentication.")
    @staticmethod    
    def deleteFromFirestore(email):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        users_ref = firestore_instance.collection('Users')

        # Query Firestore to find the document with the matching email
        query = users_ref.where('Email', '==',email)
        docs = query.stream()

        for doc in docs:
            # Delete the document from Firestore
            doc.reference.delete()
            print(f"User with email {email} deleted from Firestore.")
    @staticmethod
    def decrypt_string(encrypted_string, key='88055dab046b3213660080bc5bd4db00'):

        iv_hex, encrypted_data_hex = encrypted_string.split(':')
        iv = binascii.unhexlify(iv_hex)
        encrypted_data = binascii.unhexlify(encrypted_data_hex)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        return decrypted_data.decode('utf-8')

    
    @staticmethod
    def check_email_exists_in_firestore(email):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        # Reference to the collection
        users_ref = firestore_instance.collection('Users')

        # Query Firestore to find the document with the matching email
        query = users_ref.where('Email', '==', email)
        docs = query.stream()

        # Check if any documents match the query
        for doc in docs:
            # Email exists in Firestore
            return True

        # Email does not exist in Firestore
        return False
    

    @staticmethod
    def Login(email,password):
        email = UserController.decrypt_string(email)
        password = UserController.decrypt_string(password)

        return UserRepo.Login(email,password)
    
    @staticmethod
    def SignUp(email, Fullname, password):
        email = UserController.decrypt_string(email)
        password = UserController.decrypt_string(password)
        Fullname = UserController.decrypt_string(Fullname)
        a = UserRepo(email, Fullname, password)
        return a.add_user_to_firestore()
    
    @staticmethod
    def ChangePassword(Email,Password):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        users_ref = firestore_instance.collection('Users')

        # Query Firestore to find the document with the matching email
        query = users_ref.where('Email', '==', Email)    
        docs = query.stream()

        for doc in docs:
            # Get the reference of the document
            doc_ref = doc.reference
            
            # Update the email field with the new email value
            doc_ref.update({'Password': Password})
            print(f"Password updated successfully for user with email {Email}.")

            # Return the updated user data if needed
            updated_user_data = doc.to_dict()
            return updated_user_data

        # If no document is found for the user's email
        print(f"No document found for user with email {Email} in Firestore.")
        return None