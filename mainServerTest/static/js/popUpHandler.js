// Popup Handling
function popupPrompt() {
    document.getElementById('popup-overlay').style.display = 'block';
}

let socketID_1 = undefined;

document.addEventListener('DOMContentLoaded', function () {

    // Establish WebSocket connection
    var socket_1 = io.connect(`http://127.0.0.1:5000/`);

    socket_1.on("connect", function() {
        socketID_1 = socket_1.id;
        console.log('socket_1 ID Established: ', socketID_1)
    });

    var processedLink;
    
        // Server Update Listener
        socket_1.on('update', function(data) {
            console.log('Update from server:', data.message);
            var statusElement = document.getElementById('processingStatus');
            statusElement.innerHTML = data.message;
    
            if (data.message) {
                var progressWindow = document.getElementById('success-overlay');
                progressWindow.style.display = 'block';
            }
    
            if (data.message === 'Processing completed') {
                statusElement.innerHTML = 'Processing completed, getting info..';
                setTimeout(function() {
                    window.location.href = `/video-display?fileName=${encodeURIComponent(processedLink)}`;
                }, 2000); // Redirect to display page after 2 seconds
            }
        });

        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();

            YT_link = document.getElementById('YT_link').value;
            console.log('Link: ', YT_link);

            var form = document.getElementById('uploadForm');
            var formData = new FormData(form);

            // Append socket_1 ID to formData
            formData.append('socketID_1', socketID_1);
            console.log('Fetching with socket_1 ID: ', socketID_1)
            
            fetch('/upload-file', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Failed to upload file.');
                }
            })
            .then(data => {
                console.log('File uploaded successfully.', data);
                processedLink = data.filename;
            })
            .catch(error => {
                console.error('Error during file upload:', error);
            });
        });
})

function chooseOption(option) {
    closePopup();
    if (option === 'text') { // Text document Upload is chosen
        window.location.href = '/text-upload';
    }
    else if (option === 'video') { // Video Upload is chosen
        window.location.href = '/video-upload';
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