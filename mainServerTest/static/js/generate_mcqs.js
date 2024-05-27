// const urlParams = new URLSearchParams(window.location.search);
// const fileParam = urlParams.get('file');
// console.log(`Received File ${fileParam}`);
// const fileName = fileParam.replace(/\.[^.]+$/, '');;
// const fileUrl = `/api/files/mcqs/${encodeURIComponent(fileName)}`;

// give the stored data a variable name
const mcqsE = JSON.parse(localStorage.getItem('loadedMCQ_E') || '[]');
const mcqsM = JSON.parse(localStorage.getItem('loadedMCQ_M') || '[]');
const mcqsH = JSON.parse(localStorage.getItem('loadedMCQ_H') || '[]');



let userPoints = 0; // Initialize user points
let fetchTimeout;
async function fetchMCQs() {
    try {
        // retrieve the stored data from local storage
        const mcqsE = JSON.parse(localStorage.getItem('loadedMCQ_E') || '[]');
        const mcqsM = JSON.parse(localStorage.getItem('loadedMCQ_M') || '[]');
        const mcqsH = JSON.parse(localStorage.getItem('loadedMCQ_H') || '[]');

        const difficulty = determineDifficulty(userPoints);
        let selectedMCQs;
        if (difficulty === 'easy') {
            selectedMCQs = mcqsE;
        } else if (difficulty === 'medium') {
            selectedMCQs = mcqsM;
        } else {
            selectedMCQs = mcqsH;
        }

        // Randomly select 6 questions from the selected difficulty level
        const selectedQuestions = getRandomQuestions(selectedMCQs, 6);
        displayMCQs(selectedQuestions);
    } catch (error) {
        console.error("Failed to fetch MCQs:", error);
    }
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

function displayMCQs(mcqs) {
    const container = document.getElementById('mcq-container');
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

function getRandomQuestions(mcqs, count) {
    const shuffled = mcqs.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
}



function handleOptionClick(selectedOption, correctAnswer, optionDiv, optionsDiv) {
    const allOptions = optionsDiv.getElementsByClassName('option');
    Array.from(allOptions).forEach(option => {
        // Remove existing event listeners to prevent further clicks
        option.onclick = null;
        option.classList.remove('correct', 'incorrect');
    });

    if (selectedOption === correctAnswer) {
        optionDiv.classList.add('correct');
        updateUserPoints(true); // Increase points for correct answer
    } else {
        optionDiv.classList.add('incorrect');
        updateUserPoints(false); // Decrease points for incorrect answer
    }
    clearTimeout(fetchTimeout);
    fetchTimeout=setTimeout(fetchMCQs, 5000);
}
document.getElementById('to-leaderboard').addEventListener('click', function() {
    window.location.href = '/leaderboard'; // Assuming your leaderboard file is named 'leaderboard.html'
});
// Ensure the script runs after the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    fetchMCQs();
});