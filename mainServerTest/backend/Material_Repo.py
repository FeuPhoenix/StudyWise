from datetime import datetime
from firebase_admin import firestore
from app.Studywise.Model.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName
from app.Studywise.Model.FirestoreDB import FirestoreDB 

class Material:
    material_id=""
    user_ID=""
    file_name=""
    file_name=""
    _file_path=""
    file_type=""
    upload_date=""
    def __init__(self, material_id, user_ID, file_name, _file_path, file_type):
        self.material_id = material_id
        self.user_ID = user_ID
        self.file_name = file_name
        self._file_path = _file_path
        self.upload_date = datetime.now().strftime("%d-%B-%Y")
        self.file_type = file_type
        self.db = FirestoreDB.get_instance()
    

    @classmethod
    def fromJson(cls, data):
        return cls(
            material_id=data["material_id"],
            user_ID=data["user_ID"],
            file_name=data["file_name"],
            _file_path=data["_file_path"],
            upload_date=data["upload_date"],
            file_type=data["file_type"]
        )

    