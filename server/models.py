from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-recipes.user', '-_password_hash',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', backref='user', cascade='all, delete-orphan')

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        if not password or not isinstance(password, str):
            raise ValueError("Password must be a non-empty string.")
        self._password_hash = bcrypt.generate_password_hash(password.encode('utf-8')).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username cannot be empty.")
        if not isinstance(username, str):
            raise ValueError("Username must be a string.")
        return username

    @validates('bio')
    def validate_bio(self, key, bio):
        if bio and len(bio) > 500:
            raise ValueError("Bio cannot exceed 500 characters.")
        return bio

    def __repr__(self):
        return f"<User {self.username}>"


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50', name='min_instructions_length'),
    )

    serialize_rules = ('-user.recipes',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title cannot be empty.")
        if not isinstance(title, str):
            raise ValueError("Title must be a string.")
        if len(title) < 3:
            raise ValueError("Title must be at least 3 characters long.")
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions:
            raise ValueError("Instructions cannot be empty.")
        if not isinstance(instructions, str):
            raise ValueError("Instructions must be a string.")
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions

    @validates('minutes_to_complete')
    def validate_minutes_to_complete(self, key, minutes):
        if minutes is not None and not isinstance(minutes, int):
            raise ValueError("Minutes must be an integer or None.")
        if minutes is not None and minutes < 1:
            raise ValueError("Minutes must be a positive integer.")
        return minutes

    def __repr__(self):
        return f"<Recipe {self.title}>"