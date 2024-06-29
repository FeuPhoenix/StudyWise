let notesEdited = false;

(function($) {
    $.fn.autogrow = function(options) {
        return this.filter('textarea').each(function() {
            var self = this;
            var $self = $(self);
            var minHeight = $self.height();
            var noFlickerPad = $self.hasClass('autogrow-short') ? 0 : parseInt($self.css('lineHeight')) || 0;

            var shadow = $('<div></div>').css({
                position: 'absolute',
                top: -10000,
                left: -10000,
                width: $self.width(),
                fontSize: $self.css('fontSize'),
                fontFamily: $self.css('fontFamily'),
                fontWeight: $self.css('fontWeight'),
                lineHeight: $self.css('lineHeight'),
                resize: 'none',
                'word-wrap': 'break-word'
            }).appendTo(document.body);

            var update = function(event) {
                var times = function(string, number) {
                    for (var i = 0, r = ''; i < number; i++) r += string;
                    return r;
                };

                var val = self.value.replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/&/g, '&amp;')
                    .replace(/\n$/, '<br/>&nbsp;')
                    .replace(/\n/g, '<br/>')
                    .replace(/ {2,}/g, function(space) {
                        return times('&nbsp;', space.length - 1) + ' '
                    });

                if (event && event.data && event.data.event === 'keydown' && event.keyCode === 13) {
                    val += '<br />';
                }

                shadow.css('width', $self.width());
                shadow.html(val + (noFlickerPad === 0 ? '...' : ''));
                $self.height(Math.max(shadow.height() + noFlickerPad, minHeight));
            };

            $self.change(update).keyup(update).keydown({ event: 'keydown' }, update);
            $(window).resize(update);

            update();
        });
    };
})(jQuery);

function toggleBoard() {
    var board = document.getElementById("board");
    if (board.style.display === "none" || board.style.display === "") {
        board.style.display = "block";
        board.style.maxHeight = "800px";
    } else {
        board.style.display = "none";
    }
}

var noteTemp = '<div class="note">'
                    + '<a href="javascript:;"  class="button remove"">X</a>'
                        + '<div class="note_cnt">'
                        + '<textarea class="title" placeholder="Enter note title"></textarea>'
                        + '<textarea class="cnt" placeholder="Enter note description here"></textarea>'
                    + '</div>'
            + '</div>';

function newNote(noteData) {
    var $note = $(noteTemp).hide().appendTo("#board").show("fade", 300);

    if (noteData) {
        $note.find('textarea.title').val(noteData.title);
        $note.find('textarea.cnt').val(noteData.description);
    }

    $('.remove', $note).click(function() {
        showDeleteConfirmation($(this).parent('.note'));
    });

    $('textarea', $note).autogrow();

    // Function to add the 'focused' class to the note when textarea is focused
    function addFocus() {
        this.closest('.note').classList.add('focused');
    }

    // Function to remove the 'focused' class from the note when textarea is blurred
    function removeFocus() {
        this.closest('.note').classList.remove('focused');
    }

    // Get all textarea elements inside the newly created note
    var textareas = $note.find('textarea');

    // Add event listeners to each textarea
    textareas.each(function() {
        this.addEventListener('focus', addFocus);
        this.addEventListener('blur', removeFocus);
    });

    notesEdited = true;

    return false;
}

var notesArray = [];

async function save_notes() {
    document.getElementById('saving').style.display = 'block';
    var newNotesArray = [];

    $('.note').each(function() {
        var note = $(this);
        var noteId = new Date().getTime() + Math.floor(Math.random() * 1000); // Generating a unique ID based on the current timestamp
        var noteTitle = note.find('textarea.title').val();
        var noteDescription = note.find('textarea.cnt').val();

        var noteObject = {
            id: noteId,
            title: noteTitle,
            description: noteDescription
        };

        newNotesArray.push(noteObject);
    });

    console.log('Notes: ', newNotesArray);
    sessionStorage.setItem('notes', JSON.stringify(newNotesArray));

    var fileType = sessionStorage.getItem('fileType');
    if (fileType == 'document') {
        fileType = 'DocumentMaterial';
        console.log("File Type:\n", fileType);
    }
    else if (fileType == 'video') {
        fileType = 'VideoMaterial'
        console.log("File Type:\n", fileType);
    }

    console.log(`Saving ${urlParams.get('fileName')}'s notes...\n`, JSON.stringify(newNotesArray));

    try {
        fetch('/save-content-notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                    fileName: urlParams.get('fileName'),
                    fileType: fileType,
                    notesArray: newNotesArray
                })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            notesEdited = false;
        })
        .catch(error => console.error('Error saving notes:', error));
    }
    catch (error) {
        document.getElementById('saving').style.display = 'none';
        console.error('Error saving notes:', error);
    }

    notesArray = newNotesArray;
    
    setTimeout(() => {
        document.getElementById('saving').style.display = 'none';
        document.getElementById('saved').style.display = 'block';
    }, 500);
    
    setTimeout(() => {
        document.getElementById('saved').style.display = 'none';
    }, 2000);
}

function load_notes() {
    document.getElementById('saving').style.display = 'block';

    var thisURL = window.location.href;

    if ( thisURL.includes('/pdf-display?fileName=') ) {
        sessionStorage.setItem('fileType', 'DocumentMaterial');
        console.log("Loading notes with Type:\n", sessionStorage.getItem('fileType'));
    }
    else if ( thisURL.includes('/video-display?fileName=') ) {
        sessionStorage.setItem('fileType', 'VideoMaterial');
        console.log("Loading notes with Type:\n", sessionStorage.getItem('fileType'));
    }
    const fileType = sessionStorage.getItem('fileType')
    console.log("fileType from URL:\n", fileType);

    console.log('Loading notes...')
    fetch('/load-content-notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                fileName: urlParams.get('fileName'),
                fileType: fileType
            })
    })
    .then(response => response.json())
    .then(data => {
        if (data.data && data.data.fetchedNotes && data.data.fetchedNotes.length > 0) {
            sessionStorage.setItem('notes', JSON.stringify(data.data.fetchedNotes));
            console.log('Fetched notes: ', sessionStorage.getItem('notes'));

            notesArray = data.data.fetchedNotes;
            notesArray.forEach(function(noteData) {
                newNote(noteData);
            });

            setTimeout(() => {
                document.getElementById('saving').style.display = 'none';
                document.getElementById('saved').style.display = 'block';
            }, 500);
            
            setTimeout(() => {
                document.getElementById('saved').style.display = 'none';
            }, 2000);
        } else {
            console.log('No notes found, creating new note...')
            newNote(); // Create a new note if no saved notes are found
        }
    })
    .catch(error => console.error('Error loading notes:', error));

    setTimeout(() => {
        document.getElementById('saving').style.display = 'none';
        document.getElementById('saved').style.display = 'block';
    }, 500);
    
    setTimeout(() => {
        document.getElementById('saved').style.display = 'none';
    }, 2000);
}

var noteToDelete = null; // Variable to store the note to be deleted

function deleteNote() {
    console.log("Deleting note: ", noteToDelete)
    if (noteToDelete) {
        $(noteToDelete).hide("puff", { percent: 133 }, 250, function() {
            $(this).remove();
            save_notes(); // Save notes after deletion
            noteToDelete = null;
        });
        hideDeleteConfirmation();
    }
}

function showDeleteConfirmation(note) {
    noteToDelete = note;
    var modal = document.getElementById("delete-note-confirmation");
    modal.style.display = "block";
    document.getElementById('board').style.overflowY = 'hidden'

    // Scroll to prompt
    var modalContent = document.querySelector('.rm-note-modal-content');
    if (modalContent) {
        modalContent.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function hideDeleteConfirmation() {
    var modal = document.getElementById("delete-note-confirmation");
    modal.style.display = "none";
    document.getElementById('board').style.overflowY = 'auto'
}

$(document).ready(function() {
    $("#board").height("max-content");

    $("#add_new").click(newNote);

    load_notes(); // Load notes when the page loads

    // Save notes when the user leaves the page
    window.addEventListener('beforeunload', function() {
        save_notes();
    });

    // Event listeners for the delete confirmation modal
    $('#confirm-delete').click(deleteNote);
    $('#cancel-delete').click(hideDeleteConfirmation);

    // Hide the modal if the user clicks outside of it
    $(window).click(function(event) {
        var modal = $('#delete-note-confirmation');
        if (event.target === modal[0]) {
            hideDeleteConfirmation();
        }
        // Hide the modal when Esc key is pressed
        document.onkeydown = function(evt) {
            evt = evt || window.event;
            if (evt.keyCode == 27) {
                hideDeleteConfirmation();
            }
        };
    });

    // Dark mode toggling
    document.getElementById('NB-theme').addEventListener('click', function() {
        document.getElementById('board').classList.toggle('NB-dark');
        document.querySelectorAll('.note').forEach(function(element) {
            element.classList.toggle('dark');
        });
    });

    return false;
});