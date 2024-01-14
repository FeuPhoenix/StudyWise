var fullCards = [];
var missedCards = [];
var numberCards = 0;
var indexCounter = 0;
var successCounter = 0;
var failCounter = 0;
var isMissed = false;
//tabs
$('ul.tabs').each(function() {
    // for each set of tabs keep track of active/not
    var $active, $content, $links = $(this).find('a');
  
    // default to open on first tab
    $active = $($links.filter('[href="' + location.hash + '"]')[0] || $links[0]);
    $active.addClass('active');
  
    $content = $($active[0].hash);
  
    // hide everything else
    $links.not($active).each(function() {
      $(this.hash).hide();
    });
  
    $(this).on('click', 'a', function(e) {
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
  
  $(document).on("click", 'a', function() {
    $('a').removeClass('active');
    $(this).addClass('active');
  });
  //end tabs
  
  //flip the card when it's clicked:
  $(document).ready(
    function() {
      $(".card").flip({
        trigger: 'manual'
      });
      $(".card").click(function() {
        $(".card").flip("toggle");
      });
    }
  );
  
  //card cardsay:
  var startingCards = [{
    "front": "pwd",
    "back": "print working directory"
  }, {
    "front": "hostname",
    "back": "my computer's network name"
  }, {
    "front": "mkdir",
    "back": "make directory"
  }, {
    "front": "cd",
    "back": "change directory"
  }, {
    "front": "ls",
    "back": "list directory"
  }, {
    "front": "rmdir",
    "back": "remove directory"
  }, {
    "front": "pushd",
    "back": "push directory"
  }, {
    "front": "popd",
    "back": "pop directory"
  }, {
    "front": "cp",
    "back": "copy a file or directory"
  }, {
    "front": "robocopy",
    "back": "robust copy"
  }, {
    "front": "mv",
    "back": "move a file or directory"
  }, {
    "front": "more",
    "back": "page through a file"
  }, {
    "front": "type",
    "back": "print the whole file"
  }, {
    "front": "forfiles",
    "back": "run a command on several files"
  }, {
    "front": "select-string",
    "back": "find things inside files"
  }, {
    "front": "help",
    "back": "read a manual page"
  }, {
    "front": "echo",
    "back": "print arguments"
  }, {
    "front": "set",
    "back": "export/set a new environment variable"
  }, {
    "front": "attrib",
    "back": "change permission modifiers"
  }, {
    "front": "iCACLS",
    "back": "change ownership"
  }];
  //copying the cardsays to preserve a copy of the original
  
  for (var i=0;i<startingCards.length; i++){
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
    cardFront(index, fullCards);
    cardBack(index, fullCards); 
  }
  
var fullCards = [];
var missedCards = [];
var numberCards = 0;
var indexCounter = 0;
var successCounter = 0;
var failCounter = 0;
var isMissed = false;


function loadCards() {
  return fetch('/StudyWise/flashcards_from_pdf/JS/flash_cards.json')
    .then(response => response.json())
    .then(data => {
      fullCards = data.map(card => ({ ...card, status: "unread" }));
      numberCards = fullCards.length;
      setUp(); // Initialize the setup
    })
    .catch(error => {
      console.error('Error loading flash cards:', error);
    });
}

document.addEventListener('DOMContentLoaded', () => {
  loadCards().then(() => {
    // Additional code that needs to run after loadCards completes
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
    document.getElementById("howMany").innerHTML = "<p>" + numberCards + " cards in this deck</p>";
    console.log("fullCards at setUp:", fullCards);
    
    if (fullCards && fullCards.length > 0) {
      numberCards = fullCards.length;
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
    } else {
      console.error("fullCards is not properly initialized in setUp.");
  }
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
  
    //clear the missedcard cardsay
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
      cardFront(indexCounter, fullCards);
      cardBack(indexCounter, fullCards);
  
    } else if (successCounter === fullCards.length) {
      //when someone reaches the end of a set and got them all right!
      document.getElementById("full").innerHTML = "Retry";
      $("#full").show();
      $("#success").hide();
      $("#fail").hide();
      $("#progress").hide();
      indexCounter = 0;
      successCounter = 0;
      failCounter = 0;
      document.getElementById("successRate").innerHTML = "You killed it!!<br>Click below to retry the entire deck.";
  
      $("#successRate").show();
  
    } else if (failCounter === fullCards.length) {
      //when someone reaches the end of the set and got them all wrong
      $("#success").hide();
      $("#fail").hide();
      $("#progress").hide();
      $("#missed").hide();
      indexCounter = 0;
      failCounter = 0;
      successCounter = 0;
      document.getElementById("full").innerHTML = "Retry";
      $("#full").show();
  
      document.getElementById("successRate").innerHTML = "You missed all the cards, but practice makes perfect.";
      $("#successRate").show();
    } else {
      //when someone reaches the end of a set having missed some
      document.getElementById("successRate").innerHTML = "Known Cards: " + successCounter + "<br>" + "Missed Cards: " + failCounter;
      $("#successRate").show();
      shuffle(fullCards);
  
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
    document.getElementById("percent").innerHTML = "Card " + cardCounter + " of " + numberCards;
    document.getElementById("bar").style.width = (cardCounter / numberCards) * 100 + "%";
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
  
  //fail counter goes up by one if 'Missed it' is clicked
  document.getElementById("fail").addEventListener("click", function addOneFailCounter() {
    failCounter = failCounter + 1;
  
    //changes the button to show how many missed
    document.getElementById("fail").innerHTML = "Missed It (" + failCounter + ")";
  });
  
  document.getElementById("missed").addEventListener("click", function() {
    isMissed = true;
  });
  document.getElementById("full").addEventListener("click", function() {
    isMissed = false;
  });
  //marks card as known
  function markIfKnown() {
    if (isMissed) {
      missedCards[indexCounter].status = "known";
    } else {
      fullCards[indexCounter].status = "known";
    }
  
  }
  document.getElementById("full").addEventListener("click", function() {
    $("#success").show();
    $("#fail").show();
    $("#progress").show();
    $("#successRate").hide();
  });
  document.getElementById("missed").addEventListener("click", function() {
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

  document.addEventListener('DOMContentLoaded', () => {
  loadCards().then(() => {
    showAll();
  }
  );
}
);
