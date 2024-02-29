from datetime import datetime
from firebase_admin import firestore
from Constants.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName
from app.Studywise.Model import FirestoreDB 

class Material:
    material_id=""
    user_ID=""
    file_name=""
    file_name=""
    _file_path=""
    _file_path=""
    upload_date=""
    def __init__(self, material_id, user_ID, file_name, _file_path, upload_date, file_type):
        self.material_id = material_id
        self.user_ID = user_ID
        self.file_name = file_name
        self._file_path = _file_path
        self.upload_date = upload_date
        self.file_type = file_type
        self.db = FirestoreDB.get_instance()
    async def addMaterialToFirestore(self):
        try:
            await self.db.collection('Materials').document(kUserId).set({
                "material_id": self.material_id,
                "user_ID": self.user_ID,
                "file_name": self.file_name,
                "_file_path": self._file_path,
                "upload_date": datetime.now().strftime("%d-%B-%Y"),
                "file_type": self.file_type
            })
        except Exception as e:
            print(e)

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

    def toJson(self):
        data = {
            "material_id": self.material_id,
            "user_ID": self.user_ID,
            "file_name": self.file_name,
            "_file_path": self._file_path,
            "upload_date": self.upload_date,
            "file_type": self.file_type
        }
        return data
    async def add_material(self, material_id, user_ID, file_name, _file_path, file_type):
        try:
            upload_date = datetime.now().strftime("%d-%B-%Y")
            await self.db.collection('Materials').document(kUserId).collection('UserMaterials').document(material_id).set({
                "material_id": material_id,
                "user_ID": user_ID,
                "file_name": file_name,
                "_file_path": _file_path,
                "upload_date": upload_date,
                "file_type": file_type
            })
        except Exception as e:
            print(e)
    
    async def get_material(self, material_id):
        material_doc = await self.db.collection('Materials').document(kUserId).collection('UserMaterials').document(material_id).get()
        if material_doc.exists:
            material_data = material_doc.to_dict()
            return Material.fromJson(material_data)
        else:
            return None

    # async def update_material(self, material_id, data):
    #     try:
    #         await self.db.collection('Materials').document(material_id).update(data)
    #     except Exception as e:
    #         print(e)

    async def delete_material(self, material_id):
        try:
            await self.db.collection('Materials').document(kUserId).collection('UserMaterials').document(material_id).delete()
        except Exception as e:
            print(e)
    