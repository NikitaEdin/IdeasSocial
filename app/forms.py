from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
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