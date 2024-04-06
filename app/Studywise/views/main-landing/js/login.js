const firebaseConfig = {
    apiKey: "AIzaSyAcUOinqD6vOPhOrhIe2wB57gB1xlNPbiQ",
    authDomain: "studywise-dba07.firebaseapp.com",
    databaseURL: "https://studywise-dba07-default-rtdb.firebaseio.com",
    projectId: "studywise-dba07",
    storageBucket: "studywise-dba07.appspot.com",
    messagingSenderId: "481892684174",
    appId: "1:481892684174:web:7d4de3c274f82ced8314df",
    measurementId: "G-DDTD1ZS5LG"
};

firebase.initializeApp(firebaseConfig);

const db = firebase.firestore()

const auth = firebase.auth();
const database = firebase.database();

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const signupSuccess = urlParams.get('signup');
    
    if (signupSuccess === 'success') {
        alert('Signup successful! Please log in.');
    }
});

function signUp() {
    var fullname = document.getElementById('fullName').value;
    var email = document.getElementById('signUpEmail').value;
    var password = document.getElementById('signUpPassword').value;
    
    auth.createUserWithEmailAndPassword(email, password)
  .then(function() {
    // Declare user variable
    var user = auth.currentUser

    // Add this user to Firebase Database
    var database_ref = database.ref()

      // Validate input fields
      if (validate_email(email) == false || validate_password(password) == false) {
          alert('Email or Password is Outta Line!!')
          return
          // Don't continue running the code
      }
      if (validate_field(fullname) == false) {
          alert('One or More Extra Fields is Outta Line!!')
          return
      }

    // Create User data
    var user_data = {
        email: email,
        fullName: fullname,
        role: "user",
        userLevel: 0,
        joinedOn: firebase.firestore.FieldValue.serverTimestamp(),
        lastLogin: firebase.firestore.FieldValue.serverTimestamp()
    }

    // Push to Firebase Database
    database_ref.child('users/' + user.uid).set(user_data)

    // Done
    alert('User Created!!')
  })
  .catch(function(error) {
    // Firebase will use this to alert of its errors
    var error_code = error.code
    var error_message = error.message

    alert(error_message)
  })
}
// function signUp() {
//     var fullname = document.getElementById('fullName').value;
//     var email = document.getElementById('signUpEmail').value;
//     var password = document.getElementById('signUpPassword').value;

//     firebase.auth().createUserWithEmailAndPassword(email, password)
//         .then((userCredential) => {
//             // User Signed up
//             var user = userCredential.user;

//             return firebase.firestore().collection('users').doc(user.uid).set({
//                 "email": email,
//                 "fullName": fullname,
//                 "role": "User",
//                 "userLevel": 0,
//                 "joinedOn": firebase.firestore.FieldValue.serverTimestamp()
//             });
//         })
//         .then(() => {
//             console.log("User Created and Data Stored.")
//             // Redirect to login with success event
//             window.location.href = '/login.html?signup=success';
//         })
//         .catch((error) => {
//             var errorCode = error.code;
//             var errorMessage = error.message;
//             // Handle Errors
//             if (errorCode === 'auth/email-already-in-use') {
//                 alert('This email is already in use by another account.');
//             } else {
//                 // Handle other errors
//                 alert(errorMessage);
//             }
//         });
// }

function signIn() {
    var email = document.getElementById('signInEmail').value;
    var password = document.getElementById('signInPassword').value;

    firebase.auth().signInWithEmailAndPassword(email, password)
        .then((userCredential) => {
            // User Signed in 
            var user = userCredential.user;
        })
        .catch((error) => {
            var errorCode = error.code;
            var errorMessage = error.message;
            // Handle Errors
            alert(errorMessage);
        });
}

function validate_email(email) {
    expression = /^[^@]+@\w+(\.\w+)+\w$/
    if (expression.test(email) == true) {
        // Email is good
        return true
    } else {
        // Email is not good
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

function popupPrompt() {
    document.getElementById('popup-overlay').style.display = 'block';
}

function chooseOption(option) {
    closePopup();
    if (option === 'text') {
        window.location.href = 'upload-doc.html';
    }
    else if (option === 'video') {
        window.location.href = 'upload-video-based.html';
    }
    else {
        alert("Invalid input");
    }
}

// Close popup using 'x' button
function closePopup() {
    document.getElementById('popup-overlay').style.display = 'none';
}

// Close popup when clicking outside
window.onclick = function(event) {
    var popup = document.querySelector('.popup-overlay');
    if (event.target == popup) {
        closePopup();
    }
}

// Close popup when pressing Escape key
document.onkeydown = function(evt) {
    evt = evt || window.event;
    if (evt.keyCode == 27) {
        closePopup();
    }
};

function toggleSignUpPW() {
    var PW = document.getElementById("signUpPassword");
    var btn = document.getElementById("eye-icon1")

    if (PW.type === "password") {
        PW.type = "text";
        btn.style.color = "rgb(43, 124, 218)";
        btn.className = "fas fa-eye";
        btn.style.left = "2px";
    } 
    else {
        PW.type = "password";
        btn.style.color = "rgb(212, 39, 91)";
        btn.className = "fas fa-eye-slash";
        btn.style.left = "0";
    }
}

function toggleSigInPW() {
    var PW = document.getElementById("signInPassword");
    var btn = document.getElementById("eye-icon2")

    if (PW.type === "password") {
        PW.type = "text";
        btn.style.color = "rgb(43, 124, 218)";
        btn.className = "fas fa-eye";
        btn.style.left = "2px";
    } 
    else {
        PW.type = "password";
        btn.style.color = "rgb(212, 39, 91)";
        btn.className = "fas fa-eye-slash";
        btn.style.left = "0";
    }
}