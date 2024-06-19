let myUserContent;
window.onload = function() {
    // Fetch user name from server
    fetch('http://127.0.0.1:5000/get-user-name-JSON', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            avatar = document.querySelector('.navbar-avatar-frame');
            avatar.style.setProperty('--before-content', `'${data.userName}'`);
        })
        .then(
            fetch('http://127.0.0.1:5000/load-user-content-JSON', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                throw new Error('Network response was not ok');
                }
                return response.json(); // Parse the JSON data
            })
            .then(data => {
                if (typeof data === 'string') {
                    data = JSON.parse(data); // Parse the string if it's not an object
                }

                if (Array.isArray(data)) {
                    myUserContent = data.map(contentItem => ({
                        filename: contentItem.filename,
                        filetype: contentItem.filetype
                    }));
                    if (myUserContent.length > 0) {
                        setUpUserContent();
                        console.log('User content: ', myUserContent);
                    } else {
                        console.log('No content found');
                    }

                } else {
                    console.log('Data is not an array:', data);
                }
            })
            .catch(error => {
                console.error('Error fetching user content:', error);
            })
        )
        .catch(error => {
            console.error('Error fetching Username:', error);
        });

    // Fetch user content JSON from server
    
};
function toggleMenu() {
    const listGroup = document.querySelector('.list-group');
    listGroup.classList.toggle('show');
}
function openModal() {
    document.getElementById("nameModal").style.display = "block";
}



function closeModal() {
    document.getElementById('nameModal').style.display = 'none';
}

function openPasswordModal() {
    document.getElementById("PasswordModal").style.display = "block";
}



function closePasswordModal() {
    document.getElementById('PasswordModal').style.display = 'none';
}
$(document).ready(function() {
    $('#changeNameForm').submit(function(event) {
        event.preventDefault(); // Prevent default form submission

        var newName = $('#newName').val(); // Get the value of the new name input
        console.log(newName);
        fetch('/change_name', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ newName: newName }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Name changed successfully!');
                window.location.href = '/home'; // Redirect to index.html after success
            } else {
                alert('Failed to change name. ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to change name. Please try again.');
        });
    });
});
// Optional: Close the menu if clicked outside
document.addEventListener('click', function(event) {
    const isClickInside = document.querySelector('.navbar-avatar-frame').contains(event.target);
    if (!isClickInside) {
        document.querySelector('.list-group').style.display = 'none';
    }
});

// Close the modal when clicking outside of it
window.onclick = function(event) {
    const modal = document.getElementById('nameModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Optional: Close the menu if clicked outside
document.addEventListener('click', function(event) {
    const isClickInside = document.querySelector('.navbar-avatar-frame').contains(event.target);
    if (!isClickInside) {
        document.querySelector('.list-group').classList.remove('show');
    }
});

function logOut() {
    fetch('/log-out', {
        method: 'GET'
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url; // Redirect to the login page
        } else {
            console.error('Failed to sign out');
        }
    })
    .catch(error => {
        console.error('Error signing out:', error);
    });
}

function setUpUserContent() {

    const mainContainer = document.querySelector('.main-container');
    const contentRow = document.createElement('div');
    contentRow.classList.add('content-row');
    mainContainer.appendChild(contentRow);

    myUserContent.forEach((contentItem, index) => {

        const contentColumn = document.createElement('div');
        contentColumn.classList.add('content-column');
        contentRow.appendChild(contentColumn);

        const contentCard = document.createElement('a');
        var link;
        if (contentItem.filetype == 'mp4' || contentItem.filetype == 'YoutubeLink') {
            link = `/video-display?fileName=${encodeURIComponent(contentItem.filename)}`;
        }
        else {
            link = `/pdf-display?fileName=${encodeURIComponent(contentItem.filename)}`;
        }
        contentCard.href = link;
        contentCard.classList.add('content-card');
        contentColumn.appendChild(contentCard);

        const title = document.createElement('div');
        title.classList.add('title');
        title.textContent = contentItem.filename;
        contentCard.appendChild(title);

        const imageContainer = document.createElement('div');
        imageContainer.classList.add('image-container');
        contentCard.appendChild(imageContainer);

        const image1 = document.createElement('img');
        image1.src = "/static/assets/images/flashcards.png";
        image1.alt = "Description 1";
        image1.classList.add('flashcard-img', 'card-img');
        image1.onclick = () => imageClickHandler('Image 1');
        imageContainer.appendChild(image1);

        const image2 = document.createElement('img');
        image2.src = "/static/assets/images/summary.png";
        image2.alt = "Description 2";
        image2.classList.add('summary-img', 'card-img');
        image2.onclick = () => imageClickHandler('Image 2');
        imageContainer.appendChild(image2);

        const image3 = document.createElement('img');
        image3.src = "/static/assets/images/bot.png";
        image3.alt = "Description 3";
        image3.classList.add('bot-img', 'card-img');
        image3.onclick = () => imageClickHandler('Image 3');
        imageContainer.appendChild(image3);

        const type = document.createElement('div');
        type.classList.add('type');

        // If content is video-based, onclick will call pdf view
        if (contentItem.filetype == 'mp4' || contentItem.filetype == 'YoutubeLink') {
            // contentCard.onclick = () => contentClickHandler(contentItem.filename, 'video');
            type.textContent = 'Video';
        }
        // else (content is text-based), onclick will call video view
        else {
            // contentCard.onclick = () => contentClickHandler(contentItem.filename, 'document');
            type.textContent = 'Document';
        }
        contentCard.appendChild(type);
    });

}


function contentClickHandler(fileName, filetype) {
    if (filetype == 'document') {
        window.location.href = `/pdf-display?fileName=${encodeURIComponent(fileName)}`;
    }
    else if (filetype == 'video') {
        window.location.href = `/video-display?fileName=${encodeURIComponent(fileName)}`;
    }
    
    // If content is document, fetch its pdf view ============================= DOCUMENT ↓
    // if (filetype == 'document') {
    //     fetch('http://127.0.0.1:5000/load-document-content', {
    //             method: 'POST',
    //                     headers: {
    //                         'Content-Type': 'application/json',
    //                     },
    //                     body: JSON.stringify({fileName: fileName})
    //         })
    //         .then(response => response.json())
    //         .then(data => {
    //             const { fileName, documentLink, summary, flashcards, MCQ_E, MCQ_M, MCQ_H } = data.data;

    //             localStorage.setItem('fileName', fileName);
    //             localStorage.setItem('loadedDocumentLink', documentLink);
    //             localStorage.setItem('loadedDocumentSummary', JSON.stringify(summary));
    //             localStorage.setItem('loadedFlashcards', JSON.stringify(flashcards));
    //             localStorage.setItem('loadedMCQ_E', JSON.stringify(MCQ_E));
    //             localStorage.setItem('loadedMCQ_M', JSON.stringify(MCQ_M));
    //             localStorage.setItem('loadedMCQ_H', JSON.stringify(MCQ_H));

    //             console.log('Document Link:', localStorage.getItem('loadedDocumentLink'));
    //             console.log('Document Summary:', localStorage.getItem('loadedDocumentSummary'));
    //             console.log('Document Flashcards:', localStorage.getItem('loadedFlashcards'));
    //         })
    //         .then(() => {
    //             window.location.href = `/pdf-display`;
    //         })
    //         .catch(error => {
    //             console.error('Error fetching JSON:', error);
    //         });
    //     } // If Document END ================================================== DOCUMENT END 
        
    //     // If content is video, fetch its video view ========================== VIDEO ↓
    // else if (filetype == 'video') {c
    //     fetch('http://127.0.0.1:5000/load-video-content', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json'
    //         },
    //         body: JSON.stringify({ fileName: fileName })
    //     })
    //     .then(response => response.json())
    //     .then(data => {
    //         const { fileName, videoLink, audioLink, summary, chapters, flashcards, MCQ_E, MCQ_M, MCQ_H } = data.data;

    //         localStorage.setItem('fileName', fileName);
    //         localStorage.setItem('loadedVideoLink', videoLink);
    //         localStorage.setItem('loadedVideoAudio', audioLink);
    //         localStorage.setItem('loadedVideoSummary', JSON.stringify(summary));
    //         localStorage.setItem('loadedVideoChapters', JSON.stringify(chapters));
    //         localStorage.setItem('loadedFlashcards', JSON.stringify(flashcards));
    //         localStorage.setItem('loadedMCQ_E', JSON.stringify(MCQ_E));
    //         localStorage.setItem('loadedMCQ_M', JSON.stringify(MCQ_M));
    //         localStorage.setItem('loadedMCQ_H', JSON.stringify(MCQ_H));

    //         console.log('Video Link:', localStorage.getItem('loadedVideoLink'));
    //         console.log('Video Summary:', localStorage.getItem('loadedVideoSummary'));
    //         console.log('Video Chapters:', localStorage.getItem('loadedVideoChapters'));
    //         console.log('Video Flashcards:', localStorage.getItem('loadedFlashcards'));
    //     })
    //     .then(() => {
    //         window.location.href = `/video-display`;
    //     })
    //     .catch(error => {
    //         console.error('Error fetching Content ALL Data JSON:', error);
    //     });
    // } // else if END ====================================================== VIDEO END
}
// Change Password json
document.getElementById('changePasswordForm').addEventListener('submit', function(event) {
    var newPassword = document.getElementById('newPassword').value;
    var confirmPassword = document.getElementById('confirmPassword').value;
    
    if (newPassword !== confirmPassword) {
        alert('New password and confirm password do not match.');
        event.preventDefault(); // Prevent form submission
    }
});

// Function to toggle password visibility
function togglePasswordVisibility(inputId) {
    var input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
    } else {
        input.type = "password";
    }
}

// Event listeners for showing/hiding passwords
document.getElementById('showNewPassword').addEventListener('change', function() {
    togglePasswordVisibility('newPassword');
});

document.getElementById('showConfirmPassword').addEventListener('change', function() {
    togglePasswordVisibility('confirmPassword');
});
$(document).ready(function() {
    $('#changePasswordForm').submit(function(event) {
        event.preventDefault(); // Prevent default form submission

        var newPassword = $('#confirmPassword').val(); // Get the value of the new name input
        console.log(newPassword);
        fetch('/change_password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ newPassword: newPassword }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Passowrd changed successfully!');
                window.location.href = '/home'; // Redirect to index.html after success
            } else {
                alert('Failed to change password. ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to change password. Please try again.');
        });
    });
});
$(document).ready(function() {
    $('#deleteAccountBtn').click(function() {
        // Show confirmation dialog
        if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
            // AJAX request to delete the account
            $.ajax({
                url: '/delete_account', // Flask route for deleting account
                type: 'POST',
                success: function(response) {
                    if (response.success) {
                        alert('Account deleted successfully!');
                        window.location.href = '/login'; // Redirect to login page after success
                    } else {
                        alert('Failed to delete account: ' + response.error);
                    }
                },
                error: function(error) {
                    alert('Failed to delete account. Please try again.');
                }
            });
        }
    });
});
function imageClickHandler(image) {
    console.log(`${image} clicked`);
    event.stopPropagation(); // Prevent triggering content's click event
}