document.addEventListener("DOMContentLoaded", () => {
  const FSButton = document.querySelector(".go-fullscreen");
  const container = document.querySelector(".FC-container");
  const leaveFSButton = document.querySelector(".leave-fullscreen");
  const midrow = document.querySelector("#midrow");

  FSButton.addEventListener("click", () => {
    // Lock/Unlock interaction with other elements
    document.body.classList.toggle("locked");
    document.getElementsByTagName("html")[0].classList.toggle("locked");

    // Toggle flashcard fullscreen mode
    container.classList.toggle("fullscreen");
    midrow.classList.toggle("fullscreen");
    FSButton.classList.toggle("fullscreen");
    leaveFSButton.classList.toggle("fullscreen");

    // Keyboard Navigation only available when flashcards are in fullscreen mode
    window.addEventListener("keydown", (e) => {
      switch (e.keyCode) {
        case 37: // Left arrow (Previous card)
          currentIndex = (currentIndex === 0) ? numDictionaryItems - 1 : currentIndex - 1;
          displayCard(currentIndex);
          break;
        case 39: // Right arrow (Next card)
          currentIndex = (currentIndex === numDictionaryItems - 1) ? 0 : currentIndex + 1;
          displayCard(currentIndex);
          break;
        case 38: // Up arrow (Flag card)
          const flagButtonUp = document.getElementById("flag");
          if (!flagButtonUp.classList.contains("flagged")) {
            flagButtonUp.click();
            console.log('Your flagged cards:', flaggedCards);
          }
          break;
        case 40: // Down arrow (Unflag card)
          const flagButtonDown = document.getElementById("flag");
          if (flagButtonDown.classList.contains("flagged")) {
            flagButtonDown.click();
            console.log('Your flagged cards:', flaggedCards);
          }
          break;
        case 32: // Space bar (Flip card)
          flashcard.classList.toggle("flipped");
          break;
        case 27: // Escape (Exit fullscreen)
        
          // Lock/Unlock interaction with other elements
          document.body.classList.remove("locked");
          document.getElementsByTagName("html")[0].classList.remove("locked");

          // Toggle flashcard fullscreen mode
          container.classList.remove("fullscreen");
          midrow.classList.remove("fullscreen");
          FSButton.classList.remove("fullscreen");
          leaveFSButton.classList.remove("fullscreen");
          break;
      }
    });
  });

  // Haldling going into and out of fullscreen
  leaveFSButton.addEventListener("click", () => {
    // Lock/Unlock interaction with other elements
    document.body.classList.toggle("locked");
    document.getElementsByTagName("html")[0].classList.toggle("locked");

    // Toggle flashcard fullscreen mode
    container.classList.toggle("fullscreen");
    midrow.classList.toggle("fullscreen");
    FSButton.classList.toggle("fullscreen");
    leaveFSButton.classList.toggle("fullscreen");
  });

  // Animate fullscreen button on hover
  FSButton.addEventListener("mouseover", () => {
    document.querySelector("#midrow > button.go-fullscreen > i").classList.add("fa-beat-fade");
  });
  FSButton.addEventListener("mouseleave", () => {
    document.querySelector("#midrow > button.go-fullscreen > i").classList.remove("fa-beat-fade");
  });

  // Animate leave-fullscreen button on hover
  leaveFSButton.addEventListener("mouseover", () => {
    document.querySelector("#midrow > button.leave-fullscreen > i").classList.add("fa-beat-fade");
  });
  leaveFSButton.addEventListener("mouseleave", () => {
    document.querySelector("#midrow > button.leave-fullscreen > i").classList.remove("fa-beat-fade");
  });

  // Fetch flashcards from sessionStorage
  const loadCards = () => {
    const data = JSON.parse(sessionStorage.getItem('loadedFlashcards'));
    if (data) {
      console.log('Mapping Flashcards onto elements');
      cards = data.map(card => ({ ...card, status: "unread" }));
      numDictionaryItems = cards.length;
      displayCard(0);
    } else {
      console.error('No flashcards found in sessionStorage.');
    }
  };

  let currentIndex = 0;
  let flaggedCards = [];

  // Display the card at the specified index
  const displayCard = (index) => {
    const card = cards[index];
    document.getElementById("question").textContent = card.front;
    document.getElementById("answer").textContent = card.back;
    flashcard.classList.remove("flipped");

    // Update the flag button's state based on the current card's flagged status
    const flagButton = document.getElementById("flag");
    if (flaggedCards.includes(card)) {
      flagButton.classList.add("flagged");
    } else {
      flagButton.classList.remove("flagged");
    }
  };
  

  // Event Listeners

  var flashcard = document.getElementById("flashcard");
  flashcard.addEventListener("click", function () {
    this.classList.toggle("flipped");
  },false);

  document.getElementById("flag").addEventListener("click", function () {
    const card = cards[currentIndex];
    if (flaggedCards.includes(card)) {
      flaggedCards = flaggedCards.filter(c => c !== card);
    } else {
      flaggedCards.push(card);
    }
    this.classList.toggle("flagged");
    console.log('Your flagged cards:', flaggedCards);
  });

  document.querySelector(".prev").addEventListener("click", () => {
    currentIndex = (currentIndex === 0) ? numDictionaryItems - 1 : currentIndex - 1;
    displayCard(currentIndex);
  });

  document.querySelector(".next").addEventListener("click", () => {
    currentIndex = (currentIndex === numDictionaryItems - 1) ? 0 : currentIndex + 1;
    displayCard(currentIndex);
  });

  document.querySelector(".refresh").addEventListener("click", () => {
    cards = shuffle(cards);
    currentIndex = 0;
    displayCard(currentIndex);
  });

  // Shuffle function
  const shuffle = (cards) => {
    for (let i = cards.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [cards[i], cards[j]] = [cards[j], cards[i]];
    }
    return cards;
  };

  // Initial load
  loadCards();
});

// Placeholder JSON DATA
var cards = [
  {
    front: "front",
    back: "back",
  },
  {
    front: "front 2",
    back: "back 2",
  },
];

var numDictionaryItems = cards.length;

// Also implement these functionalities:

// left and right arrow keys - next and previous card, respectively
// up and down - flag and unflag card, respectively
// space - flip card

// Keys:
// left = 37
// right = 39
// up = 38
// down = 40
// spaceBar: 32

// PREV & NEXT BUTTONS (.prev & .next)
