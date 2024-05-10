// Popup Handling
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
        YT_link = document.getElementById('YT_link');
        window.location.href = `/process-video-link?link=${encodeURIComponent(YT_link)}`;
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