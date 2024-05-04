var chosenFile;

// Popup Handling
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
// End of Popup Handling

function handleFileSelection(input) {
    // Check if a file is selected
    if (input.files.length > 0) {
        // Get the first selected file
        var file = input.files[0];
        chosenFile = file.name;

        // Display the file name
        document.getElementById('chosen-file').textContent = 'Selected File:\n' + file.name;
        document.getElementById('chosen-file').style.visibility = 'visible'
    } else {
        // No file selected
        chosenFile = null;
        document.getElementById('chosen-file').textContent = 'No file selected';
        document.getElementById('chosen-file').style.visibility = 'hidden'
    }
}

function confirmFile() {
    // chosenFile = "";
    if (chosenFile) {
        console.log("Confirmed File: ", chosenFile, ". \n Redirecting...");
        window.location.href = 'view-video.html?file=' + encodeURIComponent(chosenFile);
    }
    else {
        alert("File Not yet Processed");
    }
}

function confirmFile() {
    if (chosenFile) {
        console.log("Selected File Name: ", chosenFile);

        var request = new XMLHttpRequest();
        request.open('POST', 'http://127.0.0.1:5000/generateContent', true);
        request.setRequestHeader('Content-Type', 'application/json');
        request.onload = function () {
            if (request.status === 200) {
                // Handle the response from the server if needed
                console.log('Filename sent successfully');
            }
        };
        request.send(JSON.stringify({ value: chosenFile }));
    }
    else {
        alert("No file selected");
    }
}
// Add dragover event listener to allow dropping files
document.getElementById('drop-area').addEventListener('dragover', function(event) {
    event.preventDefault();
    event.stopPropagation();
    // Add styling to indicate the drop area
    this.classList.add('dragover');
});

// Add drop event listener to handle dropped files
document.getElementById('drop-area').addEventListener('drop', function(event) {
    event.preventDefault();
    event.stopPropagation();
    // Remove styling from drop area
    this.classList.remove('dragover');
    // Trigger file input element with dropped files
    document.getElementById('fileElem').files = event.dataTransfer.files;
    // Handle file selection
    handleFileSelection(document.getElementById('fileElem'));
});
