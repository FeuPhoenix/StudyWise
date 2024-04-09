// Change the second argument to your options:
// https://github.com/sampotts/plyr/#options

const player = new Plyr('video', {captions: {active: true}});

// Expose player so it can be used from the console
window.player = player;

function popupPrompt() {
    document.getElementById('popup-overlay').style.display = 'block';
}

const urlParams = new URLSearchParams(window.location.search);
fileParam = urlParams.get('file');
filename = fileParam.replace(/\s/g, '_'); // Replace spaces with '_' to fetch processed results
filename = filename.replace(/\.[^.]+$/, ''); // Remove file extension
console.log('Will now fetch ('+fileParam+')\'s processed files');

if (fileParam) { // Process the 'file' that is received
    console.log("Received File Name:", filename);

    const VideoViewer = document.getElementById('video-viewer');
    VideoViewer.src = `/api/files/video-mp4/${encodeURIComponent(fileParam)}`; // Use fileParam for the Video source

    fetch(`/api/files/summaries/${filename}.json`) // Fetch summary JSON
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response error');
        }
        return response.json();
    })
    .then(jsonObject => {
        const summaryText = jsonObject.long_summary;
        document.getElementById('summaryText').innerHTML = summaryText;
    })
    .catch(error => {
        console.error('There was a problem fetching the Summary:', error);
    });

    // NOTE: FLASHCARD FETCH CODE IS IN THE FLASHCARDSV1_JS FILE

    fetch(`/api/files/indexing/${filename}.json`) // Fetch Video Indexing
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response error');
        }
        return response.json();
    })
    .then(jsonArray => {
        const indexesArray = jsonArray.map(obj => {
            // Extract values from each object
            const startValue = String(obj.start);
            const endValue = String(obj.end);
            const conciseTitleValue = String(obj.concise_title);
            // Concatenate values and return
            return startValue +' - '+ endValue +'\n'+ conciseTitleValue;
        });

        console.log("indexesArray:", indexesArray);

        // Join indexesArray with newline characters
        const indexes = indexesArray.join('\n');

        console.log("indexes: " + indexes);

        // Display concatenated values in the HTML element with id 'videoIndexes'
        document.getElementById('videoIndexes').innerHTML = indexes;
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });

    
} else {
    console.log("No input file provided.");
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