from app.extensions import db 
class Messages(db.Model):
    """
    Represents a message posted within a study group.
    """
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    group = db.relationship('StudyGroups', backref=db.backref('messages', cascade='all, delete-orphan'))
    user = db.relationship('Users', backref=db.backref('messages', cascade='all, delete-orphan'))

class GroupNotes(db.Model):
    """
    Represents collaborative notes for a study group.
    """
    __tablename__ = 'group_notes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id', ondelete='CASCADE'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    last_updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    last_updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    group = db.relationship('StudyGroups', backref=db.backref('notes', cascade='all, delete-orphan'))
    updated_by_user = db.relationship('Users', backref='group_notes')

class GroupTasks(db.Model):
    """
    Represents a task within a study group.
    """
    __tablename__ = 'group_tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id', ondelete='CASCADE'), nullable=False, index=True)
    task_description = db.Column(db.Text, nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    status = db.Column(db.String(15), nullable=False, default='pending')  # 'pending', 'in_progress', 'completed'
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    group = db.relationship('StudyGroups', backref=db.backref('tasks', cascade='all, delete-orphan'))
    assignee = db.relationship('Users', backref='assigned_tasks')

class GroupMessages(db.Model):
    """
    Represents a message sent in a study group.
    """
    __tablename__ = 'group_messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    group = db.relationship('StudyGroups', backref=db.backref('group_messages', cascade='all, delete-orphan'))
    user = db.relationship('Users', backref=db.backref('user_messages', cascade='all, delete-orphan'))
