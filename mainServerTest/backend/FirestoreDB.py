from firebase_admin import credentials, initialize_app, firestore, storage

class FirestoreDB:
    _instance = None
    def init(self):
        self._firestore_instance = firestore.client()
        self._storage_instance = storage.bucket()
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cred = credentials.Certificate("mainServerTest/backend/key.json")
            initialize_app(cred, {
    'storageBucket': 'studywise-dba07.appspot.com'
})
            cls._instance = cls()
        return cls._instance

    def get_firestore_instance(self):
        if not hasattr(self, '_firestore_instance'):
            self._firestore_instance = firestore.client()
        return self._firestore_instance

    def get_storage_instance(self):
        if not hasattr(self, '_storage_instance'):
            self._storage_instance = storage.bucket()
        return self._storage_instance