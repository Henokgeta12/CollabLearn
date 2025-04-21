const socket = io.connect('http://localhost:3000');


document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('chat-form').addEventListener('submit', function(event) 
    {
    event.preventDefault();
    sendMessage();
    });
});

function displaymessage(msg) {
    const chat = document.getElementById('message-list');
    const div = document.createElement('div');
    div.classList.add('div');
    div.innerHTML = `<strong>${msg.user}</strong>: ${msg.content} <span class="timestamp">${msg.created_at}</span>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

socket.on('welcome', function(data) {
    displaymessage({ user: "Server", content: data, created_at: new Date().toLocaleString() });
});

socket.on('chat message', function(data) {
    displaymessage(data);
});

socket.on('error', function(data) {
    displaymessage({ user: "Error", content: data, created_at: new Date().toLocaleString() });
});

function sendMessage() 
{
    const inputField = document.getElementById('message-input');
    const content = inputField.value;

    if (content.trim() === '') {
        alert("Please enter a message.");
        return false;
    }

    socket.emit('send_message', {
        group_id: groupId,
        user_id: userId,
        username: username,
        content: content
    });
    // const groupId = {{ group.id }};
    // const userId = {{ current_user.id }};
    // const username = "{{ current_user.username }}";

    displaymessage({ user: username , content: content, created_at: new Date().toLocaleString() });
    inputField.value = '';
    return false;
}
