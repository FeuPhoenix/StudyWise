from firebase_admin import credentials, initialize_app, firestore, storage
import firebase_admin
# class FirestoreDB:
#     _instance = None
#     def __init__(self):
#         self._firestore_instance = firestore.client()
#         self._storage_instance = storage.bucket()
#     @classmethod
#     def get_instance(cls):
#         if cls._instance is None:
#             cred = credentials.Certificate("mainServerTest/backend/key.json")
#             initialize_app(cred, {
#     'storageBucket': 'studywise-dba07.appspot.com'
# })
#             cls._instance = cls()
#         return cls._instance

#     def get_firestore_instance(self):
#         if not hasattr(self, '_firestore_instance'):
#             self._firestore_instance = firestore.client()
#         return self._firestore_instance

#     def get_storage_instance(self):
#         if not hasattr(self, '_storage_instance'):
#             self._storage_instance = storage.bucket()
#         return self._storage_instance
from firebase_admin import credentials, initialize_app, firestore, storage, auth
import firebase_admin

class FirestoreDB:
    _instance = None

    def __init__(self):
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
        return self._firestore_instance

    def get_storage_instance(self):
        return self._storage_instance

    @staticmethod
    def get_auth_instance():
        if not firebase_admin._apps:
            cred = credentials.Certificate("mainServerTest/backend/key.json")
            initialize_app(cred)
        return auth

    @staticmethod
    def delete_user(email):
        try:
            # Initialize auth if not already done
            auth_instance = FirestoreDB.get_auth_instance()
            
            # Retrieve the user by their email to get the UID
            user = auth_instance.get_user_by_email(email)
            print(f"User Auth: {user}")

            # Delete the user using their UID
            auth_instance.delete_user(user.uid)
            print(f"Deleted user with email {email} from Authentication.")
        except auth.UserNotFoundError:
            print(f"User with email {email} not found in Authentication.")
        except Exception as e:
            print(f"Error deleting user from Authentication: {e}")
    