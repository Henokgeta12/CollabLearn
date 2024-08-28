from app.extensions import db  # Import extensions
# Import db from app

class StudyGroups(db.Model):
    """
    Represents a study group in the platform.
    """
    __tablename__ = 'study_groups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    privacy = db.Column(db.String(10), nullable=False, default='public')  # 'public' or 'private'
    referral_code = db.Column(db.String(50), unique=True, nullable=False)  # Unique referral code

    creator = db.relationship('Users', backref=db.backref('study_groups', lazy=True, cascade="all, delete-orphan"))

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

class Notifications(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    # Relationship with Users
    user = db.relationship('Users', backref='notifications')

class GroupMemberships(db.Model):
    """
    Represents a user's membership in a study group.
    """
    __tablename__ = 'group_memberships'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    joined_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    role = db.Column(db.String(10), nullable=False, default='member')  # 'admin' or 'member'

    group = db.relationship('StudyGroups', backref=db.backref('group_memberships', cascade='all, delete-orphan'))
    user = db.relationship('Users', backref=db.backref('group_memberships', cascade='all, delete-orphan'))

class GroupResources(db.Model):
    """
    Represents a resource (file) uploaded to a study group.
    """
    __tablename__ = 'group_resources'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id', ondelete='CASCADE'), nullable=False, index=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.Text, nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    group = db.relationship('StudyGroups', backref=db.backref('group_resources', cascade='all, delete-orphan'))
    uploaded_by_user = db.relationship('Users', backref=db.backref('uploaded_resources', cascade='all, delete-orphan'))
