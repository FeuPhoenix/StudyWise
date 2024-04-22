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
    def __init__(self,user:UserRepo):
        self.db = FirestoreDB.get_instance()
        self.user=user


    