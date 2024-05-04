// StudyWise's Firebase configuration
var firebaseConfig = {
    apiKey: "AIzaSyAcUOinqD6vOPhOrhIe2wB57gB1xlNPbiQ",
    authDomain: "studywise-dba07.firebaseapp.com",
    databaseURL: "https://studywise-dba07-default-rtdb.firebaseio.com",
    projectId: "studywise-dba07",
    storageBucket: "studywise-dba07.appspot.com",
    messagingSenderId: "481892684174",
    appId: "1:481892684174:web:7d4de3c274f82ced8314df",
    measurementId: "G-DDTD1ZS5LG"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);

const db = firebase.firestore();

// Initialize variables
const auth = firebase.auth()
const database = firebase.database()

// Set up Sign Up function
function signUp() {
    // Get all our input fields
    email = document.getElementById('email').value
    password = document.getElementById('password').value
    full_name = document.getElementById('full_name').value

    // Validate inputs
    if (validate_email(email) == false) {
        alert('Invalid Email!')
        return
        // Don't continue running the code
    }
    if (validate_password(password) == false) {
        alert('Password must be at least 6 characters long!')
        return
        // Don't continue running the code
    }
    if (validate_field(full_name) == false) {
        alert('Please insert Full Name!')
        return
    }

    // Move on with Authentication
    auth.createUserWithEmailAndPassword(email, password)
        .then(function () {
            // Declare user variable
            var user = auth.currentUser

            // Add this user to Firebase Database
            var database_ref = database.ref()

            // Create User data
            var user_data = {
                email: email,
                fullName: full_name,
                role: "user",
                userLevel: 0,
                dateCreated: firebase.firestore.FieldValue.serverTimestamp(),
                lastLogin: firebase.firestore.FieldValue.serverTimestamp()
            }

            // Set data in Firestore DB
            db.collection('Users').doc(user.uid).set(user_data);

            // Push to Firebase Database
            database_ref.child('users/' + user.uid).set(user_data)

            // Done
            alert('User Created Successfully!')
        })
        .catch(function (error) {
            // Firebase will use this to alert of its errors
            var error_code = error.code
            var error_message = error.message

            alert(error_message)
        })
}

// Set up Sign In function
function signIn() {
    // Get all our input fields
    email = document.getElementById('email').value
    password = document.getElementById('password').value

    // Validate input fields
    if (validate_email(email) == false) {
        alert('Invalid Email!')
        return
    }
    if (validate_password(password) == false) {
        alert('Invalid Password!')
        return
    }

    auth.signInWithEmailAndPassword(email, password)
    .then(function () {
        // Declare user variable
        var user = auth.currentUser;

        // Realtime Database update
        var database_ref = database.ref();
        var user_data = {
            lastLogin: firebase.database.ServerValue.TIMESTAMP // For Realtime Database
        };
        database_ref.child('Users/' + user.uid).update(user_data);

        // Firestore update
        db.collection('Users').doc(user.uid).update({
            lastLogin: firebase.firestore.FieldValue.serverTimestamp() // For Firestore
        })
        .then(() => {
            console.log("Firestore lastLogin updated successfully");
        })
        .catch((error) => {
            console.error("Error updating lastLogin in Firestore: ", error);
        });

        // Done
        alert('Login Successful!');

    })
}

// Validation Functions ↓↓↓ ↓↓↓ ↓↓↓ ↓↓↓ ↓↓↓ ↓↓↓ ↓↓↓ ↓↓↓ ↓↓↓ ↓↓↓
function validate_email(email) {
    expression = /^[^@]+@\w+(\.\w+)+\w$/
    if (expression.test(email) == true) {
        // Email is valid
        return true
    } else {
        // Email is invalid
        return false
    }
}

function validate_password(password) {
    // Firebase only accepts lengths greater than 6
    if (password < 6) {
        return false
    } else {
        return true
    }
}

// Input Field must not be null
function validate_field(field) {
    if (field == null) {
        return false
    }
    if (field.length <= 0) {
        return false
    } else {
        return true
    }
}