import os
import secrets
from PIL import Image
from datetime import datetime
from app import app, db, login_manager, bcrypt
from flask_login import UserMixin
from flask import url_for
from flask_login import current_user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


######################### USER #########################
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20))
    displayname = db.Column(db.String(20))

    posts = db.relationship('Post', backref='author', lazy=True)

    # ToString
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
    # Has the password
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Check the hashed password
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    # Get user picture
    def get_pfp(self):
        image_file = url_for('static', filename='users/DefaultUser.png')
        if self.image_file:
            image_file = url_for('static', filename='profile_images/' + self.image_file)

        return image_file

    # Save picture
    def save_picture(self, form_picture):
         # Define directory where pictures are stored
        profile_images_dir = os.path.join(app.root_path, 'static/profile_images')

        # Remove previous images (if any)
        if self.image_file:
            try:
                old_picture_path = os.path.join(profile_images_dir, self.image_file)
                os.remove(old_picture_path)
            except Exception as e:
                print(f"Error removing old profile picture: {e}")
                return False


        # Generate a new filename using token_hex and keep the extension
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/profile_images', picture_fn)

        ## Attempt to save new image
        try:
            # Resize before saving
            output_size = (150, 150)
            i = Image.open(form_picture)
            i.thumbnail(output_size)

            # Save
            i.save(picture_path)
        except Exception as e:
            print(f"Error saving new profile picture: {e}")
            return False

       # Update the profile image path in the database
        self.image_file = picture_fn  # Store just the filename for database
        db.session.commit()  # Commit the changes to the database

        
        return True


    # Get full name to display, username or displayname(username)
    def get_full_name(self):
        if self.displayname:
            return f"{self.displayname} (@{self.username})"
        return self.username

######################### POSTS/TWEETS #########################
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # ToString
    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"
    




######################### PLANNED #########################
class Like(db.Model):
    __tablename__ = 'likes'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)

    # ToString
    def __repr__(self):
        return f"Like(User ID: {self.user_id}, Post ID: {self.post_id})"
    

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    # ToString
    def __repr__(self):
        return f"Comment('{self.content}', '{self.date_posted}')"