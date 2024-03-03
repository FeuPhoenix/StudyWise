from firebase_admin import credentials,initialize_app,firestore

class FirestoreDB:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cred = credentials.ApplicationDefault()
            initialize_app(cred)
            cls._instance = firestore.client()
        return cls._instance