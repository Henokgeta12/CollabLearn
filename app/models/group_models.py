from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StudyGroups(db.Model):
    """
    Represents a study group in the platform.
    """
    __tablename__ = 'study_groups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    creator = db.relationship('Users', backref=db.backref('study_groups', lazy=True))

class Messages(db.Model):
    """
    Represents a message posted within a study group.
    """
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    group = db.relationship('StudyGroups', backref=db.backref('messages', cascade='all, delete-orphan'))
    user = db.relationship('Users', backref=db.backref('messages', cascade='all, delete-orphan'))

class GroupMemberships(db.Model):
    """
    Represents a user's membership in a study group.
    """
    __tablename__ = 'group_memberships'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    joined_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    group = db.relationship('StudyGroups', backref=db.backref('group_memberships', cascade='all, delete-orphan'))
    user = db.relationship('Users', backref=db.backref('group_memberships', cascade='all, delete-orphan'))

class GroupResources(db.Model):
    """
    Represents a resource (file) uploaded to a study group.
    """
    __tablename__ = 'group_resources'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id'), nullable=False, index=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.Text, nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    group = db.relationship('StudyGroups', backref=db.backref('group_resources', cascade='all, delete-orphan'))
    uploaded_by_user = db.relationship('Users', backref=db.backref('uploaded_resources', cascade='all, delete-orphan'))
