// Popup Handling
function popupPrompt() {
    document.getElementById('popup-overlay').style.display = 'block';
}

function chooseOption(option) {
    closePopup();
    if (option === 'text') { // Text document Upload is chosen
        window.location.href = '/text-upload';
    }
    else if (option === 'video') { // Video Upload is chosen
        window.location.href = '/video-upload';
    }
    else { // Video Link is chosen
        YT_link = document.getElementById('YT_link').value;
        console.log('Link: ', YT_link);
        alert('Link in console');
        window.location.href = `/process-video-link=?link=${encodeURIComponent(YT_link)}`;
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


// Sidebar Viewer Handling
function toggleFlashcards(btn) {
    if (flashcardElement.style.display === 'none') {
        sidebarViewerElement.style.display = 'flex';
        flashcardElement.style.display = 'flex';
        btn.classList.add('active');
    } else {
        flashcardElement.style.display = 'none';
        btn.classList.remove('active');
    }
    if (flashcardElement.style.display == 'none' && summaryElement.style.display == 'none') {
        console.log('Hiding Sidebar Viewer');
        sidebarViewerElement.style.display = 'none';
        document.getElementById('main-frame').style.maxWidth = '99%';
    }
    else {
        sidebarViewerElement.style.display = 'flex';
        console.log('Showing Sidebar Viewer');
        document.getElementById('main-frame').style.maxWidth = '60%';
    }
}

function toggleSummary(btn) {
    if (summaryElement.style.display === 'none') {
        sidebarViewerElement.style.display = 'flex';
        summaryElement.style.display = 'block';
        btn.classList.add('active');
    } else {
        summaryElement.style.display = 'none';
        btn.classList.remove('active');
    }
    if (flashcardElement.style.display == 'none' && summaryElement.style.display == 'none') {
        console.log('Hiding Sidebar Viewer');
        sidebarViewerElement.style.display = 'none';
        document.getElementById('main-frame').style.maxWidth = '99%';
    }
    else {
        sidebarViewerElement.style.display = 'flex';
        console.log('Showing Sidebar Viewer');
        document.getElementById('main-frame').style.maxWidth = '60%';
    }
}

document.getElementById('toggleButton').addEventListener('click', function() {
    var videoIndexesDiv = document.getElementById('videoIndexes');
    videoIndexesDiv.classList.toggle('expanded');
    this.classList.toggle('collapsed');

    if (document.getElementById('toggleButton').title == "Show Chapters")
        document.getElementById('toggleButton').title = "Hide Chapters";
    else 
        document.getElementById('toggleButton').title = "Show Chapters";
});
