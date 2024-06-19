var fullCards = [];
var missedCards = [];
var numberCards = 0;
var indexCounter = 0;
var successCounter = 0;
var failCounter = 0;
var isMissed = false;

const flashcardElement = document.querySelector('.flashcards');
const summaryElement = document.querySelector('.summary');
const sidebarViewerElement = document.querySelector('.sidebar-viewer');
var startingCards = []; // Initialize startingCards as an empty array

// Or fetch startingCards from some source like sessionStorage
var startingCards = JSON.parse(sessionStorage.getItem('loadedFlashcards')) || [];

//tabs
$('ul.tabs').each(function () {
  // for each set of tabs keep track of active/not
  var $active, $content, $links = $(this).find('a');

  // default to open on first tab
  $active = $($links.filter('[href="' + location.hash + '"]')[0] || $links[0]);
  $active.addClass('active');

  $content = $($active[0].hash);

  // hide everything else
  $links.not($active).each(function () {
    $(this.hash).hide();
  });

  $(this).on('click', 'a', function (e) {
    // make the old tab inactive
    $active.removeClass('active');
    $content.hide();

    $active = $(this);
    $content = $(this.hash);

    // make tab active
    $active.addClass('active');
    $content.show();

    e.preventDefault();
  });
});

$(document).on("click", 'a', function () {
  $('a').removeClass('active');
  $(this).addClass('active');
});
//end tabs

//flip the card when it's clicked:
$(document).ready(
  function () {
    $(".card").flip({
      trigger: 'manual'
    });
    $(".card").click(function () {
      $(".card").flip("toggle");
    });
  }
);


for (var i = 0; i < startingCards.length; i++) {
  startingCards[i].status = "unread";
}



function shuffle(cards) {
  //derived from the Fisher-Yates Shuffle
  //https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle
  for (var i = cards.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var temp = cards[i];
    cards[i] = cards[j];
    cards[j] = temp;
  }
  return cards;
}


function displayCard(index) {
  if (index >= 0 && index < fullCards.length) {
      cardFront(index, fullCards);
      cardBack(index, fullCards);
  } else {
      console.error("Card at index", index, "is undefined.");
  }
}

function loadCards() {
  const data = JSON.parse(sessionStorage.getItem('loadedFlashcards'));
  console.log('Mapping Flashcards onto elements');
  fullCards = data.map(card => ({ ...card, status: "unread" }));
  numberCards = fullCards.length;
}

function cleanFlashcards(flashcards) {
  return flashcards.map(card => {
    return {
      front: card.front.replace(/^(Q\d*:\s*)|[0-9.\- ]+/, '').trim(), // Remove 'Q:', 'Q1:', numbers, dots, hyphens, and spaces from the beginning
      back: card.back.replace(/^(A\d*:\s*)|[0-9.\- ]+/, '').trim(),   // Remove the same things, but from 'back'
      status: card.status // Keep the status as it is
    };
  });
}

document.addEventListener('DOMContentLoaded', () => {
  let urlParams = new URLSearchParams(window.location.search);
  const fileName = urlParams.get('fileName');
  console.log(`Fetching ${fileName}'s flashcards`)
  console.log(`Flashcards in FlashcardsV1_JS:`, JSON.parse(sessionStorage.getItem('loadedFlashcards')))

  loadCards().then(() => {
    showAll();
    // show after loadCards completes
  });
});

//displays the card front
function cardFront(number, cards) {
  if (cards && cards[number]) {
    document.getElementById('front').innerHTML = cards[number].front;
  } else {
    console.error("Card at index", number, "is undefined in cardFront.");
  }
}

function cardBack(number, cards) {
  if (cards && cards[number]) {
    document.getElementById('back').innerHTML = cards[number].back;
  } else {
    console.error("Card at index", number, "is undefined in cardBack.");
  }
}

function setUp() {
  if (!fullCards || fullCards.length === 0) {
    console.error("fullCards is not properly initialized in setUp.");
    return;
  }

  numberCards = fullCards.length;
  document.getElementById("howMany").innerHTML = "<p>" + numberCards + " cards in this deck</p>";
  console.log("fullCards at setUp:", fullCards);

  shuffle(fullCards);
  displayCard(indexCounter);
  cardFront(indexCounter, fullCards);
  cardBack(indexCounter, fullCards);
  $("#full").hide();
  $("#missed").hide();
  document.getElementById("success").innerHTML = "Got It!";
  document.getElementById("fail").innerHTML = "Missed It!";
  document.getElementById("percent").innerHTML = "Card " + 1 + " of " + numberCards;
  var percentage = (1 / numberCards) * 100;
  document.getElementById("bar").style.width = percentage + "%";
}

setUp();

//this is the 're-set' of cards for someone who just wants to retry their missed cards
function setUpMissed() {
  if (missedCards.length > 0) {
    for (var j = 0; j < missedCards.length; j++) {
      if (missedCards[j].status === "known") {
        for (var k = 0; k < fullCards.length; k++) {
          if (missedCards[j].front === fullCards[k].front && missedCards[j].back === fullCards[k].back) {
            fullCards[k].status = "known";
          }
        }
      }
    }
  }

  //clear the missed cards
  missedCards.length = 0;
  for (var i = 0; i < fullCards.length; i++) {
    if (fullCards[i].status === "missed") {
      missedCards.push({
        "front": fullCards[i].front,
        "back": fullCards[i].back,
        "status": fullCards[i].status
      });
    }
  }

  successCounter = 0;
  failCounter = 0;
  indexCounter = 0;
  $("#success").show();
  $("#fail").show();
  $("#progress").show();
  $("#successRate").hide();
  $("#full").hide();
  $("#missed").hide();

  numberCards = missedCards.length;

  shuffle(missedCards);

  document.getElementById("front").innerHTML = missedCards[indexCounter].front;

  document.getElementById("back").innerHTML = missedCards[indexCounter].back;

  document.getElementById("success").innerHTML = "Got It!";
  document.getElementById("fail").innerHTML = "Missed It!";
  //progress bar 
  document.getElementById("percent").innerHTML = "Card " + 1 + " of " + numberCards;
  var percentage = (1 / numberCards) * 100;
  document.getElementById("bar").style.width = percentage + "%";

}
//when someone clicks either 'Missed it' or 'Got it' this is what progresses the cards forward
function nextCard() {
  if (indexCounter < fullCards.length - 1) {
      indexCounter += 1;
      displayCard(indexCounter);
  } else {
      console.log("End of session");
      // Hide buttons or display appropriate messages here
  }
}

function nextCardMissed() {
  //what happens when they're going through a deck:
  if (indexCounter < missedCards.length - 1) {

    indexCounter = indexCounter + 1;
    //displays the card back
    document.getElementById('front').innerHTML = missedCards[indexCounter].front;
    //displays the card back
    document.getElementById('back').innerHTML = missedCards[indexCounter].back;

  } else if (successCounter === missedCards.length) {
    //when someone reaches the end of a set and got them all right!
    document.getElementById("full").innerHTML = "Retry";
    $("#full").show();
    $("#success").hide();
    $("#fail").hide();
    $("#progress").hide();
    indexCounter = 0;
    successCounter = 0;
    failCounter = 0;
    document.getElementById("successRate").innerHTML = "You got them all! <br>Click below to retry the entire deck.";

    $("#successRate").show();

  } else if (failCounter === missedCards.length) {
    //when someone reaches the end of the set and got them all wrong
    $("#missed").show();
    $("#full").show();
    $("#success").hide();
    $("#fail").hide();
    $("#progress").hide();
    document.getElementById("successRate").innerHTML = "Known Cards: " + successCounter + "<br>" + "Missed Cards: " + failCounter + "<br>Practice makes perfect.";
    indexCounter = 0;
    failCounter = 0;
    successCounter = 0;

    $("#successRate").show();
  } else {
    //when someone reaches the end of a set having missed some
    document.getElementById("successRate").innerHTML = "Known Cards: " + successCounter + "<br>" + "Missed Cards: " + failCounter;
    $("#successRate").show();
    indexCounter = 0;
    successCounter = 0;
    failCounter = 0;
    document.getElementById("success").innerHTML = "Got It!";
    document.getElementById("fail").innerHTML = "Missed It!";
    document.getElementById("full").innerHTML = "Retry Full Set";
    $("#full").show();
    $("#missed").show();
    $("#success").hide();
    $("#fail").hide();
    $("#progress").hide();

  }
  //happens each time a person progresses through the cards
  var cardCounter = indexCounter + 1;
  document.getElementById("percent").innerHTML = "Card " + cardCounter + " of " + missedCards.length;
  document.getElementById("bar").style.width = (cardCounter / missedCards.length) * 100 + "%";
}

//a success counter goes up by 1 each time someone presses the 'got it' button
document.getElementById("success").addEventListener("click", function addOneSuccessCounter() {
  successCounter = successCounter + 1;

  //changes the button to show how many known
  document.getElementById("success").innerHTML = "Got it! (" + successCounter + ")";

});

function whichCardSet() {
  if (isMissed) {
    nextCardMissed();
  } else {
    nextCard();
  }
  // Check if all cards are done
  if (indexCounter >= fullCards.length) {
    // If all cards are done, show options to retry missed cards only or all cards
    $("#retryMissed").show();
    $("#retryAll").show();
  }
}

//fail counter goes up by one if 'Missed it' is clicked
document.getElementById("fail").addEventListener("click", function addOneFailCounter() {
  failCounter = failCounter + 1;

  //changes the button to show how many missed
  document.getElementById("fail").innerHTML = "Missed It (" + failCounter + ")";
});

document.getElementById("missed").addEventListener("click", function () {
  isMissed = true;
});
document.getElementById("full").addEventListener("click", function () {
  isMissed = false;
});
//marks card as known
function markIfKnown() {
  if (isMissed && missedCards.length > 0) {
    missedCards[indexCounter].status = "known";
  } else if (!isMissed) {
    fullCards[indexCounter].status = "known";
  }
}

document.getElementById("full").addEventListener("click", function () {
  $("#success").show();
  $("#fail").show();
  $("#progress").show();
  $("#successRate").hide();
});
document.getElementById("missed").addEventListener("click", function () {
  $("#success").show();
  $("#fail").show();
  $("#progress").show();
  $("#successRate").hide();
});
document.getElementById("success").addEventListener("click", markIfKnown);

function markIfMissed() {
  if (isMissed) {
    missedCards[indexCounter].status = "missed";
  } else {
    fullCards[indexCounter].status = "missed";
  }

}
document.getElementById("fail").addEventListener("click", markIfMissed);
document.getElementById("full").addEventListener("click", setUp);
document.getElementById("missed").addEventListener("click", setUpMissed);

function whichCardSet() {
  if (isMissed) {
    nextCardMissed();
  } else {
    nextCard();
  }
}
document.getElementById("fail").addEventListener("click", whichCardSet);
document.getElementById("success").addEventListener("click", whichCardSet);
document.getElementById("retryMissed").addEventListener("click", retryMissedCardsOnly);
document.getElementById("retryAll").addEventListener("click", retryAllCards);

//end of 'Quiz Mode'
//'Study Mode' - show all the cards in order 
function showAll() {
  var studyCardsContainer = document.getElementById('studyCards');
  studyCardsContainer.innerHTML = ''; // Clear existing content

  if (fullCards.length === 0) {
    console.error("No cards available to display.");
    return;
  }

  fullCards.forEach(card => {
    var frontDiv = document.createElement('div');
    frontDiv.className = 'card front study study-mode'; // Use the same class as in CSS
    frontDiv.innerHTML = card.front;

    var backDiv = document.createElement('div');
    backDiv.className = 'card back study study-mode'; // Use the same class as in CSS
    backDiv.innerHTML = card.back;

    studyCardsContainer.appendChild(frontDiv);
    studyCardsContainer.appendChild(backDiv);
  });
}
function retryMissedCardsOnly() {
  setUpMissed(); // Reset the missed cards setup
  isMissed = true; // Set the mode to missed cards
  $("#retryMissed").hide(); // Hide the button to avoid multiple retries
}
document.getElementById("retryMissed").addEventListener("click", retryMissedCardsOnly);


// document.addEventListener('DOMContentLoaded', () => {
// loadCards().then(() => {
//   showAll();
// });
// });
