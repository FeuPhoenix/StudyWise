from ast import List
import uuid
from app.Studywise.Constants.Constants import kUserId, kUserEmail, kDatejoined, kFullName

class Questions_Repo:
    def __init__(self,ProcessedMaterial,text: str, options: List[str], correct_answer: str):
        self.question_id=uuid.uuid4().hex
        self.text = text  # The text of the question
        self.options = options  # A list of answer options
        self.correct_answer = correct_answer  # The index of the correct option in the options list
        self.ProcessedMaterial = ProcessedMaterial
    def check_answer(self, correct_answer: str) -> bool:
        """Check if the user's selected option index is correct."""
        return correct_answer == self.correct_answer

    def get_correct_answer(self) -> str:
        """Get the correct answer text."""
        return self.options[self.correct_answer]
    def to_dict(self) -> dict:
        """Convert the question to a dictionary."""
        return {
            "text": self.text,
            "options": self.options,
            "correct_answer": self.correct_answer
        }
    async def add_question_to_firestore(self, collection_name: str):
        """Add the question as a JSON document to Firestore."""
        question_data = self.to_dict()
        # Generate a unique document ID. Alternatively, you can set your own ID.
        doc_ref = self.db.collection(kUserId).collection(self.Material.Material_id).document(self.question_id)
        await doc_ref.set(question_data)
        print(f"Question added to Firestore with ID: {doc_ref.id}")
