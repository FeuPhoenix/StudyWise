let urlParams = new URLSearchParams(window.location.search);
const fileName = urlParams.get('fileName');
document.addEventListener("DOMContentLoaded", function() {

    if (fileName) {
        document.getElementById("content-title").innerHTML = fileName;
        
        console.log('Fetching ' +fileName+ '\'s processed files');
        fetch('/load-document-content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ fileName: fileName })
        })
        .then(response => response.json())
        .then(data => {
            const { documentLink, summary, flashcards, MCQ_E, MCQ_M, MCQ_H } = data.data;

            sessionStorage.setItem('fileType', 'document');
            sessionStorage.setItem('loadedDocumentLink', documentLink);
            sessionStorage.setItem('loadedDocumentSummary', JSON.stringify(summary));
            sessionStorage.setItem('loadedFlashcards', JSON.stringify(flashcards));
            sessionStorage.setItem('loadedMCQ_E', JSON.stringify(MCQ_E));
            sessionStorage.setItem('loadedMCQ_M', JSON.stringify(MCQ_M));
            sessionStorage.setItem('loadedMCQ_H', JSON.stringify(MCQ_H));

            // console.log('Document Link:', sessionStorage.getItem('loadedDocumentLink'));
            // console.log('Document Summary:', sessionStorage.getItem('loadedDocumentSummary'));
            
            console.log('[PDF Page] Loaded Flashcards:', sessionStorage.getItem('loadedFlashcards'));
            
            // Dispatch custom load event
            const event = new Event('flashcardsLoaded');
            window.dispatchEvent(event);

            var documentURL = sessionStorage.getItem('loadedDocumentLink')
            if (documentURL) {
                const pdfViewer = document.getElementById('pdf-viewer');
                pdfViewer.src = documentURL;
        
                console.log(`Received data for fileName: ${fileName}`);
        
                const loadedDocumentSummary = JSON.parse(sessionStorage.getItem('loadedDocumentSummary'));
                const summaryText = loadedDocumentSummary.long_summary;
                console.log('Summary: ', loadedDocumentSummary.long_summary);
                document.getElementById('summaryText').innerHTML = summaryText;
        
                // NOTE: FLASHCARD FETCH CODE IS IN THE FLASHCARDSV1_JS FILE
        
                document.getElementById('loaderOverlay').style.display = 'none';
                document.getElementsByTagName("html")[0].classList.remove('locked');

            } else {
                console.log("No input file provided.");
            }
        })
        .catch(error => {
            console.error('Error fetching JSON:', error);
        });
    }
});

function goToChat() {
    if (fileName) {
        window.location.href = `/chatwithpdf?fileName=${encodeURIComponent(fileName)}`;
    } else {
        console.error("No document name found in sessionStorage");
    }
}

function goToMCQ() {
    if (fileName) {
        window.location.href = `/mcq`;
    } else {
        console.error("No document name found in sessionStorage");
    }
}

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
    }
  }
  

// Resizing the frames

// var resize = document.querySelector("#resize");
// var left = document.querySelector(".pdf-section");
// var container = document.querySelector(".page-content");
// var moveX =
// left.getBoundingClientRect().width +
// resize.getBoundingClientRect().width / 2;

// var drag = false;
// resize.addEventListener("mousedown", function (e) {
// drag = true;
// moveX = e.x;
// });

// container.addEventListener("mousemove", function (e) {
// moveX = e.x;
// if (drag) {
//     left.style.width =
//         moveX - resize.getBoundingClientRect().width / 2 + "px";
//     e.preventDefault();
// }
// });

// container.addEventListener("mouseup", function (e) {
// drag = false;
// });


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