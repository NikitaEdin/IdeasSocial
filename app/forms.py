from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Post

########### Registration
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),  Length(min=2, max=20) ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    termsCheckbox = BooleanField(' I accept the Terms and Service and Privacy Policy',validators=[DataRequired()])
    
    submit = SubmitField('Sign Up')

    # Check if username is taken
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken.')
    
    # Check if email is taken
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken.')
        

########### LOGIN
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')

    submit = SubmitField('Login')


########### POSTS
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=50)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=3, max=250)])
    submit = SubmitField('Post')

# Post comments
class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=3, max=250)])
    submit = SubmitField('Comment')

########### UPDATE USER
class ProfilePicutreForm(FlaskForm):
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Upload')

class UpdateDisplayNameForm(FlaskForm):
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=3, max=20)])
    submit = SubmitField('Update Display Name')

class UpdateEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Submit Email')

class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=3)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password', message="Passwords must match")])
    submit = SubmitField('Update Password')




