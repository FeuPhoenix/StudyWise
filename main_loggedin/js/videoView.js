// Change the second argument to your options:
// https://github.com/sampotts/plyr/#options

const player = new Plyr('video', {captions: {active: true}});

// Expose player so it can be used from the console
window.player = player;

function popupPrompt() {
    document.getElementById('popup-overlay').style.display = 'block';
}

function chooseOption(option) {
    alert('You chose: ' + option);
    // Go to choice page
    closePopup();
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