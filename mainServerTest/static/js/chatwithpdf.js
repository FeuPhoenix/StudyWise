const urlParams = new URLSearchParams(window.location.search);
const fileName = urlParams.get('fileName');

const fileUrl = sessionStorage.getItem('loadedDocumentLink');

const pdfViewer = document.getElementById('pdf-viewer');
pdfViewer.innerHTML = `<embed src="${fileUrl}" type="application/pdf" width="100%" height="600px" />`;

document.addEventListener('DOMContentLoaded', function() {
    const chat = document.getElementById('chat');
    const userInput = document.getElementById('userInput');

    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && this.value.trim() !== '') {
            const message = this.value.trim();
            displayMessage(message, 'user');
            this.value = '';

            fetch(`/chat/${encodeURIComponent(fileName)}`, {
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

    function scrollToBottom() {
        chat.scrollTop = chat.scrollHeight;
    }
    
    function displayMessage(message, sender) {
        const chat = document.getElementById('chat');  
        const messageDiv = document.createElement('div');
    
        messageDiv.classList.add('p-4', 'rounded-lg', 'my-2', 'max-w-xs');
    
        if (sender === 'user') {
            messageDiv.classList.add('bg-blue-100', 'self-end');
            messageDiv.innerHTML = formatMessage(message); // Directly format and display user messages
        } else {
            messageDiv.classList.add('bg-green-100');
            messageDiv.style.maxWidth = '25rem';
            // Apply typing effect to AI messages with formatted content
            const formattedMessage = formatMessage(message);
            typeWriter(formattedMessage, messageDiv);
        }
    
        chat.appendChild(messageDiv);
        setTimeout(scrollToBottom, 5000);
    }

    var speed = 5; // Typing speed

    function formatMessage(message) {
        // Replace newline characters with <br> tags for HTML display
        let formattedMessage = message.replace(/\n/g, "<br>");
    
        // Insert <br> before each numbered item except the first
        formattedMessage = formattedMessage.replace(/(\d+\.\s)/g, (match, p1, offset) => {
            // Do not prepend <br> to the first item
            return (offset > 0) ? `<br>${p1}` : p1;
        });
        
        // Convert **text** to <b>text</b> for bold
        formattedMessage = formattedMessage.replace(/\*\*(.*?)\*\*/g, "<b> $1 </b>");
    
        return formattedMessage;
    }

    function typeWriter(htmlContent, element, index = 0) {
        // Split the HTML content into segments of tags and text
        const segments = htmlContent.split(/(<[^>]*>)/g).filter(Boolean);
    
        // Recursive function to process each segment
        function processSegment(segIndex, charIndex) {
            // Base case: all segments are processed
            if (segIndex >= segments.length) return;
    
            const currentSegment = segments[segIndex];
            const isTag = currentSegment.startsWith('<');
    
            if (isTag) {
                // If it's an HTML tag, append it in full
                element.innerHTML += currentSegment;
                processSegment(segIndex + 1, 0); // Move to the next segment
            } else {
                // If it's text, append it character by character
                if (charIndex < currentSegment.length) {
                    element.innerHTML += currentSegment.charAt(charIndex);
                    setTimeout(() => processSegment(segIndex, charIndex + 1), speed); // Next character
                } else {
                    processSegment(segIndex + 1, 0); // Move to the next segment
                }
            }
        }
    
        // Start processing from the first segment
        processSegment(0, 0);
    }

    document.getElementById('userInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && this.value.trim() !== '') {
            const userMessage = this.value.trim();
            displayMessage(userMessage, 'user');  // Display the user's message
            displayMessage('Typing...', 'loading');  // Display the loading message
            this.value = '';
    
            fetch(`chat/${encodeURIComponent(fileName)}`, {
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
});

function removeLoadingMessage() {
    const loadingMessages = document.querySelectorAll('.message.loading');
    loadingMessages.forEach(msg => msg.remove());
}