function signUp() {
    var fullname = document.getElementById('fullName').value;
    var email = document.getElementById('signUpEmail').value;
    var password = document.getElementById('signUpPassword').value;


}

// function signIn() {
//     var email = document.getElementById('signInEmail').value;
//     var password = document.getElementById('signInPassword').value;
//     let socketID = undefined;

//     console.log('email:', email);
//     console.log('pw:', password);

//     // Establish WebSocket connection
//     var socket = io.connect('http://127.0.0.1:5000');

//     socket.on("connect", function() {
//         socketID = socket.id;
//         console.log('socketID:', socketID); // Make sure socketID is set correctly
//         const credentials = {
//             loginEmail: email,
//             loginPW: password,
//             socketID: socketID
//         };

//         fetch('http://127.0.0.1:5000/process-login', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(credentials)
//         })
//         .then(response => response.json())
//         .then(data => {
//             console.log('Server response:', data);
//             if (data.message === 'Login Successful') {
//                 console.log('UserID:', data.userID); // Assuming the server sends back the userID
//                 // Redirect or show success message
//             } else {
//                 // Handle login failure
//             }
//         })
//         .catch(error => {
//             console.error('Error during login:', error);
//             // Handle the error
//         });
//     });
    
//     socket.on('update', function(data) {
//         console.log('Update from server:', data.message);
//     });
// }


function signIn(event) { // Testing Function
    event.preventDefault();

    // Hardcoded email and password for testing
    var email = document.getElementById('signInEmail').value;
    var password = document.getElementById('signInPassword').value;
    let socketID = undefined;

    console.log('email:', email);
    console.log('pw:', password);

    // Establish WebSocket connection
    var socket = io.connect('http://127.0.0.1:5000');

    socket.on("connect", function() {
        socketID = socket.id;
        console.log('socketID:', socketID); // Make sure socketID is set correctly
        const credentials = {
            loginEmail: email,
            loginPW: password,
            socketID: socketID
        };

        fetch('http://127.0.0.1:5000/process-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(credentials)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Server response:', data);
            if (data.message === 'Login Successful') {
                console.log('UserID:', data.userID);
                // Redirect to Home Page
                setTimeout(function() {
                    window.location.href = `/pdf-display?file=${encodeURIComponent(chosenFile)}`;
                }, 3000);
            } else {
                // Handle login failure
                alert("Invalid credentials");
            }
        })
        .catch(error => {
            console.error('Error during login:', error);
            // Handle the error
        });
    });
    
    socket.on('update', function(data) {
        console.log('Update from server:', data.message);
    });
}


// Validates Email format
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

// Makes sure given password is 6 characters or more
function validate_password(password) {
    // Firebase only accepts lengths greater than 6
    if (password < 6) {
        return false
    } else {
        return true
    }
}

// Makes sure something is written in the field
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


// Toggle Password vixibility
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


// Popup Prompt Code
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

