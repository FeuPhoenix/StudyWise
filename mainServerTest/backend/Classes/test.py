from FirestoreDB import FirestoreDB


def fetch_all_data_in_collection(userid,materialid):
    db_instance = FirestoreDB.get_instance()
    firestore_instance = db_instance.get_firestore_instance()
    try:
        # Reference to the collection
        collection_ref = firestore_instance.collection("Users").document(userid).collection("VideoMaterial").document(materialid).collection("FlashCards")
        
        # Get all documents in the collection
        documents = collection_ref.get()
        
        # Initialize an empty list to store all data
        all_data = []
        
        # Iterate over each document
        for doc in documents:
            # Get the data from the document
            data = doc.to_dict()
            # Append the data to the list
            all_data.append(data)
        
        return all_data
    except Exception as e:
        print("Error:", e)
        return None
print(fetch_all_data_in_collection("3f803d991c5b490887e6992fa5e58f71","7710458347274783820eaab3812e8d9f"))