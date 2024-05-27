// Change the second argument to your options:
// https://github.com/sampotts/plyr/#options

const player = new Plyr('video', {captions: {active: true}});

const Youtube = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;

// Expose player so it can be used from the console
window.player = player;

// Load video name and video URL into const variables
const videoURL = localStorage.getItem('loadedVideoLink');
const videoName = localStorage.getItem('fileName');

// const urlParams = new URLSearchParams(window.location.search);
// videoURL = urlParams.get('URL');

console.log('Will now fetch ', videoName, '\'s processed files');
console.log('Video Link: ', videoURL);

if (videoURL) { // Process the 'file' that is received

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

    // Get the JSON object from localStorage
    const loadedVideoSummary = JSON.parse(localStorage.getItem('loadedVideoSummary'));

    // Fetch Summary
    const summaryText = loadedVideoSummary.long_summary;
    console.log('Summary: ', loadedVideoSummary.long_summary);
    document.getElementById('summaryText').innerHTML = summaryText;

    // NOTE: FLASHCARD FETCH CODE IS IN THE FLASHCARDSV1_JS FILE

    // Fetch video chapters
    try { 
            const chaptersData = JSON.parse(localStorage.getItem('loadedVideoChapters'));
            console.log('Mapping Chapters onto elements');
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

    
} else {
    console.log("No input file provided.");
}

// CHAT FOR VIDEO COMING SOON
function goToChat() {
    if (videoName) {
        alert('Chat with videos coming soon.')
        // window.location.href = `/chatwithpdf?file=${encodeURIComponent(videoName)}`;
    } else {
        console.error("No video name found in localStorage");
    }
}

function goToMCQ() {
    if (videoName) {
        window.location.href = `/mcq`;
    } else {
        console.error("No video name found in localStorage");
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