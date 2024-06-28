function toggleMenu() {
    const listGroup = document.querySelector('.list-group');
    listGroup.classList.toggle('show');
}

function openModal() {
    event.stopPropagation();
    document.getElementById("nameModal").style.display = "block";
}

function closeModal() {
    document.getElementById('nameModal').style.display = 'none';
}

function openPasswordModal() {
    event.stopPropagation();
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
                
                // Update the displayed name
                document.getElementById("usernamelabel").textContent = newName;
                
                localStorage.setItem('UserName', data.userName);
                closeModal(); // Close the modal after success
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
    const listGroup = document.querySelector('.list-group');
    const avatarFrame = document.querySelector('.navbar-avatar-frame');
    if (!avatarFrame.contains(event.target) && listGroup.classList.contains('show')) {
        listGroup.classList.remove('show');
    }
});

window.onclick = function(event) {
    const modal = document.getElementById('nameModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

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

document.getElementById('changePasswordForm').addEventListener('submit', function(event) {
    var newPassword = document.getElementById('newPassword').value;
    var confirmPassword = document.getElementById('confirmPassword').value;
    
    if (newPassword !== confirmPassword) {
        alert('New password and confirm password do not match.');
        event.preventDefault(); // Prevent form submission
    }
});

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
                alert('Password changed successfully!');
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
                url: '/delete_account',
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
                    console.error('Error:', error);
                }
            });
        }
    });
});
