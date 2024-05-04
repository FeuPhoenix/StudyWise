import datetime
import sys
from firebase_admin import firestore,auth
from FirestoreDB import FirestoreDB
from User_Repo import UserRepo
from Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName 
from flask import request,jsonify,render_template
from firebase_admin import auth

sys.path.append('D:/COLLEGE/StudyWise/app/StudyWise')

class UserController:
    @staticmethod
    def deleteUser(email):
        # Delete from Firestore
        UserController.deleteFromFirestore(email)
        
        # Delete from Authentication
        UserController.deleteFromAuthentication(email)
    @staticmethod
    def deleteFromAuthentication(email):
        try:
            # Delete the user from authentication
            user = auth.get_user_by_email(email)
            auth.delete_user()
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
    def Login(email,password):
        return UserRepo.Login(email,password)
    @staticmethod
    def SignUp(email,Fullname,password):
        a=UserRepo(email,Fullname,password)
        a.add_user_to_firestore()
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