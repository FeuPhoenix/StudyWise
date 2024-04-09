const urlParams = new URLSearchParams(window.location.search);
const fileParam = urlParams.get('file');

console.log('Fetching (' + fileParam + ')\'s processed files'); // Log fetch update

function goToChat() {
    if (fileParam) {
        window.location.href = `/chatwithpdf?file=${encodeURIComponent(fileParam)}`;
    } else {
        console.error("No file parameter found in URL.");
    }
}

function goToMCQ() {
    if (fileParam) {
        window.location.href = `/mcq?file=${encodeURIComponent(fileParam)}`;
    } else {
        console.error("No file parameter found in URL.");
    }
}

if (fileParam) {
    const filename = fileParam.replace(/\.[^.]+$/, '');
    console.log("Received File Name:", filename);

    const PDFViewer = document.getElementById('pdf-viewer');
    PDFViewer.src = `/api/files/pdf/${encodeURIComponent(fileParam)}`; // Use fileParam for the PDF source

    fetch(`/api/files/summaries/${filename}.json`) // Fetch summary JSON
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response error');
        }
        return response.json();
    })
    .then(jsonObject => {
        const summaryText = jsonObject.long;
        document.getElementById('summaryText').innerHTML = summaryText;
    })
    .catch(error => {
        console.error('There was a problem fetching the Summary:', error);
    });

    // NOTE: FLASHCARD FETCH CODE IS IN THE FLASHCARDSV1_JS FILE

} else {
    console.log("No input file provided.");
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