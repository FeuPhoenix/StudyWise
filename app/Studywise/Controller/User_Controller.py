import datetime
from firebase_admin import firestore
from Model.User import UserRepo
from Constants import Constants
from Constants.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName 
from flask import request,jsonify,render_template

class UserController:
    def __init__(self):
        self._firestore = firestore.client()
        self.userList = []
        self.userInfo = None

  
    async def addUserToFirestore(self, UserID):
        try:
            kUserId = UserID
            await self.db.collection('Users').document(kUserId).set({
                "Full Name": self.fullName,
                "Joined on": datetime.now().strftime("%d-%B-%Y"),
                "Email": self.email,
                "Role": "User",
                "User_Level": 0
            })
        except Exception as e:
            print(e)
    async def DeleteUserToFirestore(self, UserID):
        try:
            kUserId = UserID
            await self.db.collection('Users').document(kUserId).delete()
        except Exception as e:
            print(e)
    @classmethod
    def fromJson(cls, data):
        return cls(
            email=data["Email"],
            fName=data["Full Name"],
            dateJoined=data["Joined on"],
            Role=data["Role"],
            User_Level=data[0],
            
        )

    def toJson(self):
        data = {
            "Full Name": self.fullName,
            "Joined on": self.dateJoined,
            "Email": self.email,
            "Role": self.Role,
            "User_Level": self.User_Level
        }
        return data