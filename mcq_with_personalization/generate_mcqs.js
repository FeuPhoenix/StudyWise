let userPoints = 0; // Initialize user points
let fetchTimeout;
async function fetchMCQs() {
    try {
        const difficulty = determineDifficulty(userPoints);
        const response = await fetch(`output_mcqs_${difficulty}.json`);
        const mcqs = await response.json();
        displayMCQs(mcqs);
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
    window.location.href = 'leaderboard.html'; // Assuming your leaderboard file is named 'leaderboard.html'
});
// Ensure the script runs after the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    fetchMCQs();
});
