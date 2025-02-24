// Connect to Socket.IO
const socket = io.connect('http://' + document.domain + ':' + location.port);

// Listen for messages from the server
socket.on('receive_message', function(data) {
    const messageList = document.getElementById('message-list');
    const newMessage = document.createElement('div');
    newMessage.classList.add('message');
    newMessage.innerHTML = `<strong>${data.user}</strong>: ${data.content} <span class="timestamp">${data.created_at}</span>`;
    messageList.appendChild(newMessage);
    messageList.scrollTop = messageList.scrollHeight; // Scroll to the bottom
});

// Send message function
function sendMessage() 
{
    const content = document.querySelector('input[name="content"]').value;

    // Check if the message content is not empty
    if (content.trim() === '') {
        alert("Please enter a message.");
        return false; // Prevent the form from submitting
    }

    // Emit the message to the server
    socket.emit('send_message', {
        group_id: group.id ,
        content: content
    });

    // Clear the input field
    document.querySelector('input[name="content"]').value = '';

    return false; // Prevent form submission
}