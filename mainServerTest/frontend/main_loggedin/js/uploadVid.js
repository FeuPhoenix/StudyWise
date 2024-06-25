var chosenFile;
let socketID = undefined;

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

// function confirmFile() {
//     if (chosenFile) {
//         console.log("Selected File Name: ", chosenFile);

//         // Establish WebSocket connection
//         var socket = io.connect('http://127.0.0.1:5000/');

//         socket.on("connect", function() {
//             socketID = socket.id;
//         })

//         var statusElement = document.getElementById('processingStatus');

//         // Listen for 'update' events from the server to get real-time processing updates
//         socket.on('update', function(data) {
//             console.log('Update from server:', data.message);
//             statusElement.innerHTML = data.message; // Update UI

//             if (data.message) {
//                 progressWindow = document.getElementById('success-overlay')
//                 progressWindow.style.display = 'block';
//             }
        
//             // Check if the received message is 'Processing completed'
//             if (data.message === 'Processing completed') {
//                 statusElement.innerHTML = 'Processing completed, getting info';
//                 setTimeout(function() {
//                     window.location.href = `/video-display?file=${encodeURIComponent(chosenFile)}`;
//                 }, 3000); // Redirect to display page after 3 seconds
//             }
//         });

//         // Set up XMLHttpRequest to send the filename to the server
//         var request = new XMLHttpRequest();
//         request.open('POST', 'http://127.0.0.1:5000/generateVideoContent', true);
//         request.setRequestHeader('Content-Type', 'application/json');
//         request.onload = function() {
//             // Handle response from server
//             if (!(request.status >= 200 && request.status < 400)) {
//                 console.log('Server returned an error:', request.status);
//             }
//         };
//         request.onerror = function() {
//             console.log('Request failed to reach the server');
//         };
        
//         // Send the filename as JSON
//         request.send(JSON.stringify({ filename: chosenFile, socketID: socketID }));
//     } else {
//         alert("No file selected");
//     }
// }