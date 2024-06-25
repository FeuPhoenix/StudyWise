let chosenFile;
let socketID = undefined;

let inputFile; // Define formData globally
let input;

function handleFileSelection() {
    input = document.getElementById('file');
    var chosenFileLabel = document.getElementById('chosen-file');
    chosenFileLabel = document.getElementById('chosen-file');
    chosenFile = input.files[0];
    input.files[0].name = null;
    
    // Check if a file is selected
    if (input.files.length > 0) {
        console.log('Ready to upload document!');
        // Get the first selected file

        chosenFileLabel.textContent = 'Selected File: ' + chosenFile.name;
        chosenFileLabel.style.visibility = 'visible';
    } else {
        // No file selected
        chosenFile = null;
        document.getElementById('chosen-file').textContent = 'No file selected';
        document.getElementById('chosen-file').style.visibility = 'hidden';
    }
}

document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();

    var form = document.getElementById('uploadForm');
    var formData = new FormData(form);

    // Append File type
    formData.append('FileType', 'document');

    fetch('/upload-file', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            console.log('File uploaded successfully.');
            response.text().then(text => console.log(text));

            // Send the file name to the server
            var fileInput = document.getElementById('file');
            var fileName = fileInput.files[0].name;

            fetch('/filename', {
                method: 'POST',
                body: JSON.stringify({ filename: fileName }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                if (response.ok) {
                    console.log('File name sent to server.');
                } else {
                    console.error('Failed to send file name to server.');
                }
            });
        } else {
            console.error('Failed to upload file.');
        }
    });
});


// function confirmFile() {
//     if (chosenFile) {
        
//         // Fetch the URL from the Flask server
//         fetch('/upload-file', {
//             method: 'POST',
//             body: {file: inputFile, FileType: 'document'},
//         })
//         .then(response => {
//             if (response.ok) {
//                 console.log('FILE UPLOADING')
//                 return response.json();
//             } else {
//                 throw new Error('Failed to upload file');
//             }
//         })
//         .then(data => {
//             // Handle the response from the server
//             console.log('FILE UPLOADED SUCCESSFULLY:', data);
//         })
//         .catch(error => {
//             // Handle any errors that occur during the fetch request
//             console.error('ERROR UPLOADING FILE:', error);
//         });

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