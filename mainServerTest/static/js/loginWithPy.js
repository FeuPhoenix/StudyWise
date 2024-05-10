// const crypto = require('crypto-browserify');
async function encryptString(stringToEncrypt, key) {
    const keyBuffer = await crypto.subtle.importKey(
        'raw', 
        new TextEncoder().encode(key),
        { name: 'AES-CBC' },
        false,
        ['encrypt']
    );

    const iv = crypto.getRandomValues(new Uint8Array(16));
    const encryptedBuffer = await crypto.subtle.encrypt(
        { name: 'AES-CBC', iv },
        keyBuffer,
        new TextEncoder().encode(stringToEncrypt)
    );

    const encryptedArray = Array.from(new Uint8Array(encryptedBuffer));
    const encryptedHex = encryptedArray.map(byte => ('00' + byte.toString(16)).slice(-2)).join('');
    const ivHex = Array.from(iv).map(byte => ('00' + byte.toString(16)).slice(-2)).join('');

    return ivHex + ':' + encryptedHex;
}

async function signUp() {
    event.preventDefault();

    var fullname = document.getElementById('fullName').value;
    var email = document.getElementById('signUpEmail').value;
    var password = document.getElementById('signUpPassword').value;

    const cKey='88055dab046b3213660080bc5bd4db00';

    var encryptedEmail = email;
    var encryptedPW = password;
    var encryptedName = fullname;


    // var encryptedEmail = await encryptString(email, cKey);
    // var encryptedPW = await encryptString(password, cKey);
    // var encryptedName = await encryptString(fullname, cKey);

    console.log('email:', encryptedEmail);
    console.log('pw:', encryptedPW);
    console.log('fName:', encryptedName);

    let socketID = undefined;

    // Establish WebSocket connection
    var socket = io.connect('http://127.0.0.1:5000/');

    socket.on("connect", function() {
        socketID = socket.id;
        console.log('socketID:', socketID); // Make sure socketID is set correctly
        const credentials = {
            signupEmail: encryptedEmail,
            signupPW: encryptedPW,
            fName: encryptedName,
            socketID: socketID
        };

        fetch('http://127.0.0.1:5000/process-signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(credentials)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Server response:', data);
            update = data.message;
            if (update == 'Signup Success') {
                console.log('Signed up, logging user in...');
                document.getElementById('loginSuccessOverlay').style.display = 'block';
                document.getElementById('loginSuccessMSG').innerHTML = 'Signed up, logging user in';

                // Redirect to home page after 3 seconds
                setTimeout(function() {
                    window.location.href = '/home';
                }, 3000);
            } 
            else if (update == 'User already exists') { // Handle User already exists error
                alert(update);
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

// function signIn() {
//     var email = document.getElementById('signInEmail').value;
//     var password = document.getElementById('signInPassword').value;
//     let socketID = undefined;

//     console.log('email:', email);
//     console.log('pw:', password);

//     // Establish WebSocket connection
//     var socket = io.connect('http://127.0.0.1:5000/');

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

async function signIn(event) { // Testing Function
    event.preventDefault();

    // Hardcoded email and password for testing
    var email = document.getElementById('signInEmail').value;
    var password = document.getElementById('signInPassword').value;

    const cKey='88055dab046b3213660080bc5bd4db00';

    var encryptedEmail = email;
    var encryptedPW = password;

    // var encryptedEmail = await encryptString(email, cKey);
    // var encryptedPW = await encryptString(password, cKey);

    let socketID = undefined;

    // encryptString(email, cKey)
    // .then((encryptedEmail) => {
    //     console.log('email:', encryptedEmail);
    //     return encryptString(password, cKey);
    // })
    // .then((encryptedPW) => {
    //     console.log('pw:', encryptedPW);
    // })
    // .catch((error) => {
    //     console.error('Encryption error:', error);
    // });

    // Establish WebSocket connection
    var socket = io.connect('http://127.0.0.1:5000/');

    socket.on("connect", function() {
        socketID = socket.id;
        console.log('socketID:', socketID); // Make sure socketID is set correctly
        const credentials = {
            loginEmail: encryptedEmail,
            loginPW: encryptedPW,
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
            update = data.message;
            if (update == 'Login Success') { // Login Success
                console.log('Signing user in...');
                document.getElementById('loginSuccessOverlay').style.display = 'block';

                // Redirect to home page after 3 seconds
                setTimeout(function() {
                    window.location.href = '/home';
                }, 3000);
            }
            else if (update == 'Failed Login attempt') { // Invalid credentials
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
    if (option === 'text') { // Text document Upload is chosen
        window.location.href = 'upload-doc.html';
    }
    else if (option === 'video') { // Video Upload is chosen
        window.location.href = 'upload-video-based.html';
    }
    else { // Video Link is chosen
        window.location.href = 'upload-video-based.html';
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