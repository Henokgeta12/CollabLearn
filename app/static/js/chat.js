// Connect to Socket.IO
const socket = io.connect('http://localhost:3000');

const username = "{current_user.username}";
const group_id = "{group_id}";
const userId = "{{ current_user.id }}";

function displaymessage(msg) 
{
    const chat = document.getElementById('message-list');
    const div = document.createElement('div');
    div.classList.add('div');
    div.innerHTML = `<strong>${msg.user}</strong>: ${msg.content} <span class="timestamp">${msg.created_at}</span>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight; // Scroll to the bottom
}

socket.on('welcome', function(data) 
{
    displaymessage(data);
})
// Listen for messages from the server
socket.on('chat message', function(data) {
    displaymessage(data);
});

// Listen for messages from the server
socket.on('error', function(data) {
    displaymessage(data);
});

function displaymessage(msg) 
{
    const chat = document.getElementById('message-list');
    const div = document.createElement('div');
    div.classList.add('div');
    div.innerHTML = `<strong>${msg.user}</strong>: ${msg.content} <span class="timestamp">${msg.created_at}</span>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}
// Send message function
function sendMessage(data) 
{
    const content = document.querySelector('input[name="content"]').value;

    // Check if the message content is not empty
    if (content.trim() === '') {
        alert("Please enter a message.");
        return false; // Prevent the form from submitting
    }

    // Emit the message to the server
    socket.emit('send_message', {
        group_id: groupId,
        user_id: userId,
        username: username,
        content: content
    });

    // Clear the input field
    document.querySelector('input[name="content"]').value = '';

    return false; // Prevent form submission
}