#needs to be improved
from datetime import datetime
from firebase_admin import firestore
from Constants.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName
from app.Studywise.Controller.Video_Processed_Controller import Video_Processed_Controller 

# Assuming the Materials and Processed_Materials classes are defined in app.Studywise.Model
from app.Studywise.Model import FirestoreDB, Material_Repo, VideoProcessed_Repo

class Flash_Cards:
    def __init__(self, flashcard_id, flashhcard_json_file,):
        self.flashcard_id = flashcard_id  # Removed the comma at the end
        self.flashhcard_json_file=flashhcard_json_file
        self.db = FirestoreDB.get_instance()
    async def addFlashCardsToFirestore(self):
        
        processed_data = self.processed_material  # Assuming Processed_Materials has a method named 'process'
        #.document(self.processed_material.user_id)
        try:
            await self.db.collection('UsersFlashCards').document(kUserId).collection(self.processed_material.processed_material_id).document(self.flashcard_id
                                                                                                                                 ).set({
                "flashcard_id": self.flashcard_id,
                "flashhcard_json_file":self.flashhcard_json_file
                
            })
        except Exception as e:
            print(e)

    @classmethod
    def fromJson(cls, data, processed_material):
        # Assuming you also want to pass a Processed_Materials object when creating from JSON
        return cls(
            flashcard_id=data.get("flashcard_id", ""),
         # Pass the Processed_Materials object here
        )

    def toJson(self):
        return {
            "flashcard_id": self.flashcard_id,
            
            
        }
    