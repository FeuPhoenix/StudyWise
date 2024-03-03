var chosenFile;

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

function togglesignupPW() {
    var PW = document.getElementById("pw1");
    var btn = document.getElementById("eye-icon1")

    if (PW.type === "password") {
        PW.type = "text";
        btn.style.color = "rgb(43, 124, 218)";
        btn.className = "fas fa-eye";
    } 
    else {
        PW.type = "password";
        btn.style.color = "rgb(212, 39, 91)";
        btn.className = "fas fa-eye-slash";
    }
}

function togglesiginPW() {
    var PW = document.getElementById("pw2");
    var btn = document.getElementById("eye-icon2")

    if (PW.type === "password") {
        PW.type = "text";
        btn.style.color = "rgb(43, 124, 218)";
        btn.className = "fas fa-eye";
    } 
    else {
        PW.type = "password";
        btn.style.color = "rgb(212, 39, 91)";
        btn.className = "fas fa-eye-slash";
    }
}