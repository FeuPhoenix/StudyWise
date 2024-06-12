from Notes_Repo import Notes
from FirestoreDB import FirestoreDB
class Notes_Controller:
    @staticmethod
    def Add_Notes_tofirestore(JsonData,userid,materialid,Type,MaterialName):
        N=Notes(JsonData,userid,materialid,Type,MaterialName)
        N.addNotesToFirestore()
    @staticmethod
    def fetch_notes_if_exist(user_id, material_type, material_id):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        try:
            # Reference to the document
            doc_ref = firestore_instance.collection('Users').document(user_id).collection(material_type).document(material_id)
            
            # Fetch the document
            doc = doc_ref.get()
            
            if doc.exists:
                doc_data = doc.to_dict()
                if "notes" in doc_data:
                    print("Notes found:", doc_data["notes"])
                    return doc_data["notes"]
                else:
                    print("Notes do not exist in the document.")
                    return None
            else:
                print("Document does not exist.")
                return None
            
        except Exception as e:
            print("An error occurred:", e)
            return None