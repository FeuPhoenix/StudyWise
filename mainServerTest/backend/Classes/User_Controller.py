import sys
import time
from firebase_admin import firestore,auth
from firebase_admin import auth
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii

from backend.Classes.FirestoreDB import FirestoreDB
from backend.Classes.User_Repo import UserRepo

sys.path.append('D:/COLLEGE/StudyWise/app/StudyWise')

class UserController:
    @staticmethod
    def deleteUser(user_id, email):
        # Delete from Firestore
        print("entered delete user")
        print(email)
        UserController.deleteFromFirestore(user_id)
        print("finished delete from firestore")
        # Delete from Authentication
        time.sleep(1)
        UserController.deleteFromAuthentication(user_id)
        print("finished delete from authentication")

    @staticmethod
    def deleteFromFirestore(user_id):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        users_ref = firestore_instance.collection('Users')
        
        doc_ref = users_ref.document(user_id)
        doc = doc_ref.get()
        print("A7a Deleteing the user",user_id)
        if doc.exists:
            doc_ref.delete()
            time.sleep(1)
            print(f"Deleted user with ID {user_id} from Firestore.")
        else:
            print(f"No document found for user with ID {user_id} in Firestore.")

    # @staticmethod
    # def deleteFromAuthentication(user_id):
    #     try:
    #         # Assuming you have a method to delete the user from the authentication system by user ID
    #         auth_instance = AuthenticationService.get_instance()
    #         auth_instance.delete_user(user_id)
    #         print(f"Deleted user with ID {user_id} from Authentication.")
    #     except Exception as e:
    #         print(f"Error deleting user from Authentication: {e}")
    @staticmethod
    def get_password_by_email(email):
        return UserRepo.get_password_by_email(email)

    @staticmethod
    def send_password_reset_email(email):
        try:

            # Initialize auth if not already done
            auth_instance = FirestoreDB.get_auth_instance()
            
            # Generate a password reset link
            reset_link = auth_instance.generate_password_reset_link(email)
            print(f"Password reset link generated: {reset_link}")
            print(f"Password reset link sent to: {email}")
        except auth.UserNotFoundError:
            print(f"User with email {email} not found in Authentication.")
        except Exception as e:
            print(f"Error sending password reset email: {e}")
    @staticmethod
    def deleteFromAuthentication(id):
        try:
            # Delete the user from authentication
            # user = auth.get_user_by_email(email)
            auth.delete_user(id)
            # print("user Auth",user)
            print(f"User with email  deleted from Authentication.")
        except auth.UserNotFoundError:
            print(f"User with email  not found in Authentication.")
    # @staticmethod    
    # def deleteFromFirestore(email):
    #     db_instance = FirestoreDB.get_instance()
    #     firestore_instance = db_instance.get_firestore_instance()

    #     users_ref = firestore_instance.collection('Users')

    #     # Query Firestore to find the document with the matching email
    #     query = users_ref.where('Email', '==',email)
    #     docs = query.stream()

    #     for doc in docs:
    #         # Delete the document from Firestore
    #         doc.reference.delete()
    #         print(f"User with email {email} deleted from Firestore.")
    @staticmethod
    def decrypt_string(encrypted_string, key='88055dab046b3213660080bc5bd4db00'):

        iv_hex, encrypted_data_hex = encrypted_string.split(':')
        iv = binascii.unhexlify(iv_hex)
        encrypted_data = binascii.unhexlify(encrypted_data_hex)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        return decrypted_data.decode('utf-8')

    
    @staticmethod
    def check_email_exists_in_firestore(email):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        # Reference to the collection
        users_ref = firestore_instance.collection('Users')

        # Query Firestore to find the document with the matching email
        query = users_ref.where('Email', '==', email)
        docs = query.stream()

        # Check if any documents match the query
        for doc in docs:
            # Email exists in Firestore
            return True

        # Email does not exist in Firestore
        return False
    

    @staticmethod
    def Login(email,password):
        # email = UserController.decrypt_string(email)
        # password = UserController.decrypt_string(password)

        return UserRepo.Login(email,password)
    @staticmethod
    def changeName(userid,name):
        return UserRepo.update_user_name_by_id(userid,name)
    @staticmethod
    def SignUp(email, Fullname, password):
        # email = UserController.decrypt_string(email)
        # password = UserController.decrypt_string(password)
        # Fullname = UserController.decrypt_string(Fullname)
        a = UserRepo(email, Fullname, password)
        return a.add_user_to_firestore()
    
    def ChangePassword(doc_id, new_password):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        users_ref = firestore_instance.collection('Users')

        try:
            # Retrieve the document with the matching document ID
            doc_ref = users_ref.document(doc_id)
            doc = doc_ref.get()

            if doc.exists:
                # Update the document with the new password
                doc_ref.update({'Password': new_password})
                print(f"Password updated successfully for user with ID {doc_id}.")

                # Return the updated user data if needed
                updated_user_data = doc.to_dict()
                return updated_user_data

            # If no document is found with the given document ID
            print(f"No document found with ID {doc_id} in Firestore.")
            return None

        except Exception as e:
            print(f"Error updating password for document ID {doc_id}: {e}")
            return None
def main():
    UserController.send_password_reset_email("abdelrahman0213@gmail.com")

if __name__ == '__main__':
    main()

     