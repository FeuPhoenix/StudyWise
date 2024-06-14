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
    + '<a href="javascript:;" class="button remove">X</a>'
    + '<div class="note_cnt">'
    + '<textarea class="title" placeholder="Enter note title"></textarea>'
    + '<textarea class="cnt" placeholder="Enter note description here"></textarea>'
    + '</div>'
    + '</div>';

var noteZindex = 1;
var noteToDelete = null; // Variable to store the note to be deleted

function showDeleteConfirmation(note) {
    noteToDelete = note;
    var modal = document.getElementById("delete-confirmation");
    modal.style.display = "block";
}

function hideDeleteConfirmation() {
    var modal = document.getElementById("delete-confirmation");
    modal.style.display = "none";
}

function deleteNote() {
    if (noteToDelete) {
        $(noteToDelete).hide("puff", { percent: 133 }, 250, function() {
            $(this).remove();
            save_notes(); // Save notes after deletion
        });
        hideDeleteConfirmation();
    }
}

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

    return false;
}

function save_notes() {
    var notesArray = [];

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

        notesArray.push(noteObject);
    });

    localStorage.setItem('notes', JSON.stringify(notesArray));
    console.log("Saving Notes...\n", JSON.stringify(notesArray));
}

function load_notes() {
    var savedNotes = localStorage.getItem('notes');
    if (savedNotes) {
        var notesArray = JSON.parse(savedNotes);
        notesArray.forEach(function(noteData) {
            newNote(noteData);
        });
    } else {
        newNote(); // Create a new note if no saved notes are found
    }
}

$(document).ready(function() {
    $("#board").height("max-content");

    $("#add_new").click(newNote);

    load_notes(); // Load notes from local storage when the page loads

    // Save notes when the user leaves the page
    window.onbeforeunload = function() {
        save_notes();
    };

    // Event listeners for the delete confirmation modal
    $('#confirm-delete').click(deleteNote);
    $('#cancel-delete').click(hideDeleteConfirmation);

    // Hide the modal if the user clicks outside of it
    $(window).click(function(event) {
        var modal = $('#delete-confirmation');
        if (event.target === modal[0]) {
            hideDeleteConfirmation();
        }
    });

    return false;
});