from flask import request, jsonify
from flask_socketio import emit, join_room
from app.models.group_models import Messages, StudyGroups
from app.extensions import socketio, db
from flask_login import current_user

@socketio.on('join')
def on_join(data):
    """Handles when a user joins a group room."""
    group_id = data['group_id']
    join_room(group_id)
    
    # Notify other users in the room that a new user has joined
    emit('user_joined', {'user': current_user.username}, room=group_id)

@socketio.on('send_message')
def handle_send_message(data):
    """Handles sending messages in real-time."""
    group_id = data['group_id']
    content = data['content']

    try:
        # Save message to the database
        new_message = Messages(
            group_id=group_id,
            user_id=current_user.id,
            content=content
        )
        db.session.add(new_message)
        db.session.commit()

        # Emit the message to all clients in the room
        emit('receive_message', {
            'user': current_user.username,
            'content': content,
            'created_at': new_message.created_at.strftime('%Y-%m-%d %H:%M')
        }, room=group_id)

    except Exception as e:
        # Handle any exceptions, such as database errors
        emit('error', {'error': str(e)}, room=group_id)
