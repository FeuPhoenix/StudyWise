const urlParams = new URLSearchParams(window.location.search);
const fileParam = urlParams.get('file');
const fileUrl = `/api/files/pdf/${encodeURIComponent(fileParam)}`;

const pdfViewer = document.getElementById('pdf-viewer');
pdfViewer.innerHTML = `<embed src="${fileUrl}" type="application/pdf" width="100%" height="700px" />`;

document.addEventListener('DOMContentLoaded', function() {
    const chat = document.getElementById('chat');
    const userInput = document.getElementById('userInput');

    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && this.value.trim() !== '') {
            const message = this.value.trim();
            displayMessage(message, 'user');
            this.value = '';

            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            })
            .then(response => response.json())
            .then(data => {
                displayMessage(data.response, 'ai');
            })
            .catch(error => console.error('Error:', error));
        }
    });

    function displayMessage(message, sender) {
        const chat = document.getElementById('chat');  // Assuming 'chat' is the ID of your chat container
    
        // Create a new div element for the message
        const messageDiv = document.createElement('div');
        messageDiv.textContent = message;  // Set the text content to the message
    
        // Add common message classes
        messageDiv.classList.add('p-4', 'rounded-lg', 'my-2', 'max-w-xs');
    
        // Add sender-specific styles
        if (sender === 'user') {
            messageDiv.classList.add('bg-blue-100', 'self-end');  // Tailwind classes for user messages
        } else {
            messageDiv.classList.add('bg-green-100');  // Tailwind classes for AI messages
        }
    
        // Append the new message div to the chat container
        chat.appendChild(messageDiv);
    
        // Scroll to the bottom of the chat container to show the latest message
        chat.scrollTop = chat.scrollHeight;
    }
    
});

document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && this.value.trim() !== '') {
        const userMessage = this.value.trim();
        displayMessage(userMessage, 'user');  // Display the user's message
        displayMessage('Typing...', 'loading');  // Display the loading message
        this.value = '';

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage }),
        })
        .then(response => response.json())
        .then(data => {
            removeLoadingMessage();  // Remove the loading message
            displayMessage(data.response, 'bot');  // Display the bot's response
        })
        .catch(error => {
            removeLoadingMessage();  // Ensure loading message is removed even if there's an error
            console.error('Error:', error);
        });
    }
});

function removeLoadingMessage() {
    const loadingMessages = document.querySelectorAll('.message.loading');
    loadingMessages.forEach(msg => msg.remove());
}

