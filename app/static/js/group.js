var socket = io.connect('http://' + document.domain + ':' + location.port);

// Join the room
socket.emit('join', {'group_id': {{ group.id }}});

// Listen for incoming messages
socket.on('receive_message', function(data) {
    var messageList = document.getElementById('message-list');
    var newMessage = document.createElement('div');
    newMessage.classList.add('message');
    newMessage.innerHTML = `<strong>${data.user}</strong>: ${data.content} <span class="timestamp">${data.created_at}</span>`;
    messageList.appendChild(newMessage);
});

// Handle form submission
var form = document.querySelector('form');
form.onsubmit = function(event) {
    event.preventDefault();
    var content = document.querySelector('textarea[name="content"]').value;
    socket.emit('send_message', {'group_id': {{ group.id }}, 'content': content});
    form.reset();
};