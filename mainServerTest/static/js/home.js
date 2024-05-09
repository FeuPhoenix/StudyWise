window.onload = function() {
    // Fetch user name from server
    fetch('http://127.0.0.1:5000/get-user-name-JSON', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('User: ', data.userName);
            avatar = document.querySelector('.navbar-avatar-frame');
            avatar.style.setProperty('--before-content', `'${data.userName}'`);
        })
        .catch(error => {
            console.error('Error fetching Username:', error);
        });

    // Fetch user content JSON from server
    
};

function signOut() {
    fetch('/sign-out', {
        method: 'GET'
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url; // Redirect to the login page
        } else {
            console.error('Failed to sign out');
        }
    })
    .catch(error => {
        console.error('Error signing out:', error);
    });
}

function contentClickHandler(content) {
    console.log(`${content} clicked`);
}

function imageClickHandler(image) {
    console.log(`${image} clicked`);
    event.stopPropagation(); // Prevent triggering content's click event
}

// Popup Handling
function popupPrompt() {
    document.getElementById('popup-overlay').style.display = 'block';
}

function chooseOption(option) {
    closePopup();
    if (option === 'text') {
        window.location.href = '/text-upload';
    }
    else if (option === 'video') {
        window.location.href = '/video-upload';
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
// End of Popup Handling