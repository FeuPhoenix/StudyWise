from firebase_admin import credentials, initialize_app, storage

class firebaseStorage:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cred = credentials.Certificate("app/Studywise/key.json")
            initialize_app(cred, {
                'storageBucket': 'studywise-dba07.appspot.com'
            })
            
            #'storageBucket': 'studywise-dba07.appspot.com'
            cls._instance = storage.bucket()
        return cls._instance