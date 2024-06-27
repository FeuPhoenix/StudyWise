const mcqsE = JSON.parse(sessionStorage.getItem('loadedMCQ_E') || '[]');
const mcqsM = JSON.parse(sessionStorage.getItem('loadedMCQ_M') || '[]');
const mcqsH = JSON.parse(sessionStorage.getItem('loadedMCQ_H') || '[]');
const allMcqs = [...mcqsE, ...mcqsM, ...mcqsH];

let userPoints = 0; // Initialize user points
let fetchTimeout;
let answeredCount = 0; // Variable to track the number of answered questions

function fetchMCQs() {
    try {
        const difficulty = determineDifficulty(userPoints);
        let selectedMCQs;
        if (difficulty === 'easy') {
            selectedMCQs = mcqsE;
        } else if (difficulty === 'medium') {
            selectedMCQs = mcqsM;
        } else {
            selectedMCQs = mcqsH;
        }

        const selectedQuestions = getRandomQuestions(selectedMCQs, 6);
        answeredCount = 0; // Reset the answered count
        displayMCQs(selectedQuestions, 'mcq-container');
    } catch (error) {
        console.error("Failed to fetch MCQs:", error);
    }
}

function fetchAllMCQs() {
    displayMCQs(allMcqs, 'mcq-container-general');
}

function displayMCQs(mcqs, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = ''; // Clear previous content

    mcqs.forEach((mcq, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.classList.add('question');
        questionDiv.textContent = `${index + 1}. ${mcq.question}`;

        const optionsDiv = document.createElement('div');
        mcq.options.forEach((option, optionIndex) => {
            const optionDiv = document.createElement('div');
            optionDiv.classList.add('option');
            optionDiv.textContent = `${String.fromCharCode(65 + optionIndex)}. ${option}`;
            optionDiv.onclick = () => handleOptionClick(option, mcq.correct_answer, optionDiv, optionsDiv);
            optionsDiv.appendChild(optionDiv);
        });

        container.appendChild(questionDiv);
        container.appendChild(optionsDiv);
    });
}

function updateUserPoints(correct) {
    if (correct) {
        userPoints += 10;
    } else {
        userPoints -= 5; // Optional: Decrease points for an incorrect answer
    }
    userPoints = Math.max(userPoints, 0); // Ensure points don't go negative
    displayUserPoints();
}

function displayUserPoints() {
    const pointsDisplay = document.getElementById('user-points');
    pointsDisplay.textContent = `Points: ${userPoints}`;
}

function determineDifficulty(points) {
    if (points < 50) return 'easy';
    else if (points < 100) return 'medium';
    else return 'hard';
}

function getRandomQuestions(mcqs, count) {
    const shuffled = mcqs.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
}

function handleOptionClick(selectedOption, correctAnswer, optionDiv, optionsDiv) {
    const allOptions = optionsDiv.getElementsByClassName('option');
    Array.from(allOptions).forEach(option => {
        option.onclick = null; // Remove click event listener to prevent further clicks
        option.classList.remove('correct', 'incorrect');
    });

    if (selectedOption === correctAnswer) {
        optionDiv.classList.add('correct');
        updateUserPoints(true);
    } else {
        optionDiv.classList.add('incorrect');
        updateUserPoints(false);
        // Highlight the correct answer
        Array.from(allOptions).forEach(option => {
            if (option.textContent.endsWith(correctAnswer)) {
                option.classList.add('correct');
            }
        });
    }
    answeredCount++; // Increment the answered count

    // Check if all questions are answered
    const totalQuestions = document.querySelectorAll('.question').length;
    if (answeredCount === totalQuestions) {
        clearTimeout(fetchTimeout);
        fetchTimeout = setTimeout(fetchMCQs, 5000);
    }
}

document.getElementById('to-leaderboard').addEventListener('click', function() {
    window.location.href = '/leaderboard';
});

document.addEventListener('DOMContentLoaded', function() {
    fetchMCQs();
    fetchAllMCQs();
});

function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}
