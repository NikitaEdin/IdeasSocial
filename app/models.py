import os
import secrets
from PIL import Image
from datetime import datetime, timezone
from app import app, db, login_manager, bcrypt
from flask_login import UserMixin
from flask import url_for
from flask_login import current_user
from sqlalchemy import func
import re

# Global/static variables
MAX_CONTENT_LENGTH = 100 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User Follow
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Follow follwer_id={self.follower_id} followed_id={self.followed_id}>"
    

######################### USER #########################
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20))
    displayname = db.Column(db.String(20))
    bio = db.Column(db.String(250))
    # IS ADMIN
    admin_status = db.Column(db.Boolean, default=False)

    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    # Followers, users that follow THIS user
    followers = db.relationship('Follow',foreign_keys=[Follow.followed_id],backref='followed_user',lazy='dynamic')

    # Follwings, the users that THIS user follows
    following = db.relationship( 'Follow',foreign_keys=[Follow.follower_id], backref='follower_user',lazy='dynamic')

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
    
    # Check if THIS user is following the given user
    def is_following(self, user):
        return self.following.filter_by(followed_id=user.id).first() is not None
    
    # Check if user is followed by given user
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None
    

    def get_suggested_users(current_user, limit=5):
        # Subquery to get user ids that current user is currently following
        followed_user_subquery = db.session.query(Follow.followed_id).filter_by(follower_id=current_user.id)

        # Query to get users with the most followers, that are not yet followed by current user
        suggested_users = (
            db.session.query(User)
            .outerjoin(Follow, Follow.followed_id == User.id)
            .filter(User.id.notin_(followed_user_subquery), User.id != current_user.id)
            .group_by(User.id)
            .order_by(func.count(Follow.follower_id).desc()) # sort by follower count
            .limit(limit)
            .all()
        )
        return suggested_users

    # Get total followers
    def get_follower_count(self):
        return self.followers.count()
    # Get total post count
    def get_post_count(self):
        return len(Post.query.filter_by(user_id=self.id).order_by(Post.date_posted.desc()).all())


    # Is Admin?
    def is_admin(self):
        return self.admin_status

######################### POSTS related #########################
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Link with Likes and Comments
    likes = db.relationship('Like', backref='post', lazy='dynamic')
    comments = db.relationship('Comment', backref='post', lazy=True)


    # ToString
    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"
    
    # Like count, total
    def like_count(self):
        return self.likes.count()

    # os liked by given user
    def is_liked_by_user(self, user):
        return Like.query.filter_by(user_id=user.id, post_id=self.id).first() is not None
    
    # Get all hashtags within post content
    def extract_hashtags(self):
        hashtags = re.findall(r'#([\w-]+)', self.content)
        return hashtags
    
    # Converts plain text tags into interactible links
    def content_with_links(self, shortended=False):
        if shortended:
            content_with_links = self.shortened_content(MAX_CONTENT_LENGTH)
        else:
            content_with_links = self.content

        for hashtag in self.extract_hashtags():
            hashtag_link = f'<a href="/search?query=%23{hashtag}" class="hashtag">#{hashtag}</a>'
            content_with_links = content_with_links.replace(f'#{hashtag}', hashtag_link)
        return content_with_links
    
    # Limit the visible content
    def get_content_snippet(self, max_length=MAX_CONTENT_LENGTH):
        if len(self.content) > max_length:
            return self.content[:max_length] + '...'
        return self.content

    # Shorten content to nearest whitespace 
    # To avoid broken and unsafe structures (prevent page from breaking)
    def shortened_content(self, max_length=MAX_CONTENT_LENGTH):
        if len(self.content) <= max_length:
            return self.content
        
        truncated = self.content[:max_length]
        last_space_index = truncated.rfind(' ')

        # Return the content up to the last space
        if last_space_index != -1:
            return truncated[:last_space_index] + '...'
        else:
            return truncated + '...'


    
# Post comments
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    # ToString
    def __repr__(self):
        return f"Comment('{self.content}', '{self.date_posted}')"


# Post Likes
class Like(db.Model):
    __tablename__ = 'likes'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)

    # ToString
    def __repr__(self):
        return f"Like(User ID: {self.user_id}, Post ID: {self.post_id})"
    

