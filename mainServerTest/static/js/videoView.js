let urlParams = new URLSearchParams(window.location.search);

document.addEventListener("DOMContentLoaded", function() {
    const fileName = urlParams.get('fileName');

    if (fileName) {
        document.getElementById("content-title").innerHTML = fileName;

        console.log('Fetching ' +fileName+ '\'s processed files');

        fetch('http://127.0.0.1:5000/load-video-content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ fileName: fileName })
        })
        .then(response => response.json())
        .then(data => {
            const { videoLink, audioLink, summary, chapters, flashcards, MCQ_E, MCQ_M, MCQ_H } = data.data;

            sessionStorage.setItem('fileType', 'video');
            sessionStorage.setItem('loadedVideoLink', videoLink);
            sessionStorage.setItem('loadedVideoAudio', audioLink);
            sessionStorage.setItem('loadedVideoSummary', JSON.stringify(summary));
            sessionStorage.setItem('loadedVideoChapters', JSON.stringify(chapters));
            sessionStorage.setItem('loadedFlashcards', JSON.stringify(flashcards));
            sessionStorage.setItem('loadedMCQ_E', JSON.stringify(MCQ_E));
            sessionStorage.setItem('loadedMCQ_M', JSON.stringify(MCQ_M));
            sessionStorage.setItem('loadedMCQ_H', JSON.stringify(MCQ_H));

            // console.log('Video Link:', sessionStorage.getItem('loadedVideoLink'));
            // console.log('Video Audio:', sessionStorage.getItem('loadedVideoAudio'));
            // console.log('Video Summary:', sessionStorage.getItem('loadedVideoSummary'));
            // console.log('Video Chapters:', sessionStorage.getItem('loadedVideoChapters'));
            // console.log('Video Flashcards:', sessionStorage.getItem('loadedFlashcards'));

            const videoURL = sessionStorage.getItem('loadedVideoLink')
            if (videoURL) { // Load the video content that is received

                if (Youtube.test(videoURL)) {
                    const youtubeURL = videoURL;
                    const playerSource = {
                        type: 'video',
                        sources: [
                            {
                                src: youtubeURL,
                                provider: 'youtube',
                            },
                        ],
                    };
                    player.source = playerSource;
                }
                else {
                    const VideoViewer = document.getElementById('video-viewer');
                    VideoViewer.src = videoURL; // Use videoURL for the Video source
                }
            
                // Get the JSON object from sessionStorage
                const loadedVideoSummary = JSON.parse(sessionStorage.getItem('loadedVideoSummary'));
            
                // Fetch Summary
                const summaryText = loadedVideoSummary.long_summary;
                console.log('Summary: ', loadedVideoSummary.long_summary);
                document.getElementById('summaryText').innerHTML = summaryText;
            
                // NOTE: FLASHCARD FETCH CODE IS IN THE FLASHCARDSV1_JS FILE
            
                // Fetch video chapters and map them into html element
                try { 
                        const chaptersData = JSON.parse(sessionStorage.getItem('loadedVideoChapters'));
                        console.log('Mapping Chapters into element');
                        const indexesArray = chaptersData.map(obj => {
                            const startValue = String(obj.start);
                            const endValue = String(obj.end);
                            let conciseTitleValue = String(obj.concise_title);
                        
                            if (conciseTitleValue.startsWith("Title: ")) {
                                conciseTitleValue = conciseTitleValue.slice(7); // Remove "Title: "
                            }
                        
                            return startValue + ' - ' + endValue + '\n' + conciseTitleValue;
                        });
                
                    console.log("indexesArray:", indexesArray);
                
                    const indexes = indexesArray.join('\n');
                
                    console.log("indexes: " + indexes);
                
                    document.getElementById('videoIndexes').innerHTML = indexes;
                } catch (error) {
                    console.error('Error loading chapters:', error);
                }

                document.getElementById('loaderOverlay').style.display = 'none';
                document.getElementsByTagName("html")[0].style.overflowY = 'auto';
                
            } else {
                console.log("No input file provided.");
            }
            
        })
        .catch(error => {
            console.error('Error fetching JSON:', error);
        });
    }
});

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
  

const player = new Plyr('video', {captions: {active: true}});

const Youtube = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;

// Expose player so it can be used from the console
window.player = player;


document.getElementById('toggleButton').addEventListener('click', function() {
    var videoIndexesDiv = document.getElementById('videoIndexes');
    videoIndexesDiv.classList.toggle('expanded');
    this.classList.toggle('collapsed');

    if (document.getElementById('toggleButton').title == "Show Chapters")
        document.getElementById('toggleButton').title = "Hide Chapters";
    else 
        document.getElementById('toggleButton').title = "Show Chapters";
});

// CHAT FOR VIDEO COMING SOON
function goToChat() {
    if (videoName) {
        alert('Chat with videos coming soon.')
        // window.location.href = `/chatwithpdf?file=${encodeURIComponent(videoName)}`;
    } else {
        console.error("No video name found in sessionStorage");
    }
}

function goToMCQ() {
    if (videoName) {
        window.location.href = `/mcq`;
    } else {
        console.error("No video name found in sessionStorage");
    }
}

function bypassCORS(link) {
   return fetch(`https://cors-anywhere.herokuapp.com/${link}`, {
    headers: {
        'x-requested-with': 'XMLHttpRequest'
    }
   })
  .then(response => response.json())
  .then(data => console.log(data));
}

function returnURL(url) {
    console.log(url);
    return fetch(`/proxy?url=${url}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response error');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error fetching data:', error);
    });
}

// Popup Handling                           POPUP
function popupPrompt() {
    document.getElementById('popup-overlay').style.display = 'block';
}
//                                          POPUP
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

// Close popup using 'x' button             POPUP
function closePopup() {
    document.getElementById('popup-overlay').style.display = 'none';
}

// Close popup when clicking outside        POPUP
window.onclick = function(event) {
    var popup = document.querySelector('.popup-overlay');
    if (event.target == popup) {
        closePopup();
    }
}

// Close popup when pressing Escape key     POPUP
document.onkeydown = function(evt) {
    evt = evt || window.event;
    if (evt.keyCode == 27) {
        closePopup();
    }
};