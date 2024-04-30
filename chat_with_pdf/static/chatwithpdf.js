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
                if (data.error) {
                    displayMessage(data.error, 'error');
                } else {
                    displayMessage(data.response, 'ai');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                displayMessage('Failed to send message.', 'error');
            });
        }
    });

    document.getElementById('upload-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData();
        const fileInput = document.getElementById('file-input');
        formData.append('file', fileInput.files[0]);

        fetch('/upload', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayPDF(data.fileUrl);
            } else if (data.error) {
                displayMessage(data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayMessage('Failed to upload PDF.', 'error');
        });
    });

    function displayPDF(fileUrl) {
        const pdfViewer = document.getElementById('pdf-viewer');
        pdfViewer.innerHTML = `<embed src="${fileUrl}" type="application/pdf" width="100%" height="800px" />`;
    }

    function displayMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.textContent = message;
        
        messageDiv.classList.add('p-4', 'rounded-lg', 'my-2', 'max-w-xs', 'text-white');
        
        if (sender === 'user') {
            messageDiv.classList.add('bg-blue-500', 'self-end');
        } else if (sender === 'ai') {
            messageDiv.classList.add('bg-green-500');
        } else if (sender === 'error') {
            messageDiv.classList.add('bg-red-500');
        }
        
        chat.appendChild(messageDiv);
        chat.scrollTop = chat.scrollHeight;
    }
});
