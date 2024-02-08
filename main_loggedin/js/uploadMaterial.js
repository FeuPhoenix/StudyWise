var chosenFile;

function popupPrompt() {
    document.getElementById('popup-overlay').style.display = 'block';
}

function chooseOption(option) {
    alert('You chose: ' + option);
    // Go to choice page
    closePopup();
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
    if (chosenFile) {
        console.log("Selected File Name:", chosenFile);

        var request = new XMLHttpRequest();
        request.open('POST', 'http://127.0.0.1:5000/makeFlashcards', true);
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

