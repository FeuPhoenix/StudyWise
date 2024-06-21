var chosenFile;
let socketID = undefined;

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
//             console.log("Socket ID: ", socketID);
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
//                     window.location.href = `/pdf-display?file=${encodeURIComponent(chosenFile)}`;
//                 }, 3000); // Redirect to display page after 3 seconds
//             }
//         });

//         // Set up XMLHttpRequest to send the filename to the server
//         var request = new XMLHttpRequest();
//         request.open('POST', 'http://127.0.0.1:5000/generateTextContent', true);
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

// function confirmFile() {
//     // Giive a static test filename and the socket ID
//     const filename = 'test.txt';
//     let socketID;

//     const socket = io.connect('http://127.0.0.1:5000/');

//     socket.on('connect', () => {
//         socketID = socket.id;
//         console.log(`Connected with socket ID: ${socketID}`);
//     });
    
//     // Request body
//     const data = {
//     filename: filename,
//     socketID: socketID
//     };

//     // Make a POST request to the Flask route
//     fetch('http://127.0.0.1:5000/generateTextContent', {
//     method: 'POST',
//     headers: {
//         'Content-Type': 'application/json'
//     },
//     body: JSON.stringify(data)
//     })
//     .then(response => {
//     if (!response.ok) {
//         throw new Error('Network response was not ok');
//     }
//     return response.json();
//     })
//     .then(data => {
//     console.log(data);
//     })
//     .catch(error => {
//     console.error('There was a problem with your fetch operation:', error);
//     });

// }