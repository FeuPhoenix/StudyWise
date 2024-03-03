from datetime import datetime
import uuid
from firebase_admin import firestore

from app.Studywise.Model import FirestoreDB


class UserRepo:
    
    def __init__(self,email, fullName, dateJoined=None, Role=None,User_Level=0 ):
        self.email = email
        self.fullName = fullName
        self.dateJoined = dateJoined
        self.Role = Role
        self.User_Level=User_Level
        self.userID=uuid.uuid4().hex
        self.db = FirestoreDB.get_instance()
    async def addUserToFirestore(self, UserID):
        try:
            kUserId = UserID
            await self.db.collection('Users').document(UserID).set({
                "Full Name": self.fullName,
                "Joined on": datetime.now().strftime("%d-%B-%Y"),
                "Email": self.email,
                "Role": "User",
                "User_Level": 0
            })
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
    