import requests
from backend.Classes.Notes_Repo import Notes
from backend.Classes.FirestoreDB import FirestoreDB
class Notes_Controller:

    @staticmethod
    def Add_Notes_tofirestore(JsonData, userid, Type, MaterialName):
        N = Notes(JsonData, userid, Type, MaterialName)
        N.addNotesToFirestore()

    @staticmethod
    def fetch_json_from_url(url):
            try:
                # Make a GET request to download the JSON file
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for any HTTP error status codes
                
                # Load the JSON data
                data = response.json()
                return data
            except requests.exceptions.RequestException as e:
                print("Error:  2", e)
                return None
            
    @staticmethod
    def fetch_notes_if_exist(user_id, material_type, MaterialName):
        Material_id=Notes.Retrieve_MaterialID(user_id, material_type, MaterialName)
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        try:
            # Reference to the document
            doc_ref = firestore_instance.collection('Users').document(user_id).collection(material_type).document(Material_id)
            
            # Fetch the document
            doc = doc_ref.get()
            
            if doc.exists:
                doc_data = doc.to_dict()
                if "notes" in doc_data:
                    print("Notes found:", doc_data["notes"])
                    return Notes_Controller.fetch_json_from_url(doc_data["notes"])
                else:
                    print("Notes do not exist in the document.")
                    return None
            else:
                print("Document does not exist.")
                return None
            
        except Exception as e:
            print("An error occurred:", e)
            return None