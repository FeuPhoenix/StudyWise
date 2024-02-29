#needs to be improved
from datetime import datetime
from firebase_admin import firestore
from Constants.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName
from app.Studywise.Controller.Video_Processed_Controller import Video_Processed_Controller 

# Assuming the Materials and Processed_Materials classes are defined in app.Studywise.Model
from app.Studywise.Model import Material, VideoProcessed

class Flash_Cards:
    def __init__(self, flashcard_id, front_content, back_content, processed_material,):
        self.flashcard_id = flashcard_id  # Removed the comma at the end
        self.front_content = front_content  # Removed the comma at the end
        self.back_content = back_content  # Removed the comma at the end
        self.processed_material = processed_material  # This is the Processed_Materials object
        self.creation_date = datetime.now().strftime("%d-%B-%Y")
        self.db = firestore.client()

    async def addFlashCardsToFirestore(self):
        
        processed_data = self.processed_material  # Assuming Processed_Materials has a method named 'process'
        #.document(self.processed_material.user_id)
        try:
            await self.db.collection('UsersFlashCards').document(kUserId).collection(self.processed_material.processed_material_id).document(self.flashcard_id
                                                                                                                                 ).set({
                "flashcard_id": self.flashcard_id,
                "front_content": self.front_content,
                "back_content": self.back_content,
                "creation_date": self.creation_date,
            })
        except Exception as e:
            print(e)

    @classmethod
    def fromJson(cls, data, processed_material):
        # Assuming you also want to pass a Processed_Materials object when creating from JSON
        return cls(
            flashcard_id=data.get("flashcard_id", ""),
            front_content=data.get("front_content", ""),
            back_content=data.get("back_content", ""),  # Pass the Processed_Materials object here
        )

    def toJson(self):
        return {
            "flashcard_id": self.flashcard_id,
            "front_content": self.front_content,
            "back_content": self.back_content,
            "creation_date": self.creation_date,
            
        }
    