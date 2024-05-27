// const urlParams = new URLSearchParams(window.location.search);
// const fileParam = urlParams.get('file');

const documentURL = localStorage.getItem('loadedDocumentLink');
const documentName = localStorage.getItem('fileName');
console.log('Fetching ' + documentName + '\'s processed files'); // Log fetch update


if (documentURL) {
    const pdfViewer = document.getElementById('pdf-viewer');
    pdfViewer.src = documentURL;

    const fileName = localStorage.getItem('fileName');
    console.log(`Received data for fileName: ${fileName}`);

    const loadedDocumentSummary = JSON.parse(localStorage.getItem('loadedDocumentSummary'));
    const summaryText = loadedDocumentSummary.long_summary;
    console.log('Summary: ', loadedDocumentSummary.long_summary);
    document.getElementById('summaryText').innerHTML = summaryText;

    // NOTE: FLASHCARD FETCH CODE IS IN THE FLASHCARDSV1_JS FILE

} else {
    console.log("No input file provided.");
}

function goToChat() {
    if (documentName) {
        window.location.href = `/chatwithpdf`;
    } else {
        console.error("No document name found in localStorage");
    }
}

function goToMCQ() {
    if (documentName) {
        window.location.href = `/mcq`;
    } else {
        console.error("No document name found in localStorage");
    }
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