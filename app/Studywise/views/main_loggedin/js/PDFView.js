var chosenFile;

const urlParams = new URLSearchParams(window.location.search);
fileParam = urlParams.get('file');
//filename = fileParam.replace(/\s/g, '_'); // Replace spaces with '_' to fetch processed results
filename = fileParam.replace(/\.[^.]+$/, ''); // Remove file extension
console.log('Will now fetch ('+fileParam+')\'s processed files');

if (fileParam) { // Process the 'file' that is received
    console.log("Received File Name:", filename);

    // CHANGE THIS LATER TO POTENTIALLY REMOVE THE WHOLE FETCH OPERATION AND 
    // JUST ATTEMPT TO SET PDF SRC TO THE FILE PATH
    fetch('../../../../app/assets/input_files/text_based/'+filename+'.pdf') // 1) Fetch PDF
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response error');
        }
        var PDF = document.getElementById('pdf-viewer');
        PDF.src = '../../../../app/assets/input_files/text_based/'+filename+'.pdf';
        return response.json();
    })
    .catch(error => {
        console.error('There was a problem fetching the PDF:', error);
    });

    fetch('../../../../app/assets/output_files/summaries/'+filename+'.json') // 2) Fetch Summary
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

    // THIS IS COMMENTED BECAUSE IT WAS A PLACEHOLDER WITH VIDEO INDEXING FETCH CODE
    // THE FLASHCARD FETCH CODE IS IN THE FLASHCARDSV1_JS FILE

    // fetch('../../../../app/assets/output_files/flashcards/'+filename+'.json') //3) Fetch Flashcards
    // .then(response => {
    //     if (!response.ok) {
    //         throw new Error('Network response error');
    //     }
    //     return response.json();
    // })
    // .then(jsonArray => {
    //     const indexesArray = jsonArray.map(obj => {
    //         // Extract values from each object
    //         const startValue = String(obj.start);
    //         const endValue = String(obj.end);
    //         const conciseTitleValue = String(obj.concise_title);
    //         // Concatenate values and return
    //         return startValue +' - '+ endValue +'\n'+ conciseTitleValue;
    //     });

    //     console.log("indexesArray:", indexesArray);

    //     // Join indexesArray with newline characters
    //     const indexes = indexesArray.join('\n');

    //     console.log("indexes: " + indexes);

    //     // Display concatenated values in the HTML element with id 'videoIndexes'
    //     document.getElementById('videoIndexes').innerHTML = indexes;
    // })
    // .catch(error => {
    //     console.error('There was a problem fetching the Flashcards:', error);
    // });

    
} else { // No input file
    console.log("No input file provided.");
}

// Popup Handling
function popupPrompt() {
    document.getElementById('popup-overlay').style.display = 'block';
}

function chooseOption(option) {
    closePopup();
    if (option === 'text') {
        window.location.href = 'upload-doc.html';
    }
    else if (option === 'video') {
        window.location.href = 'upload-video-based.html';
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