from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User
from flask_login import login_user, current_user, logout_user

# Global/static variables
POSTS_PER_PAGE = 5

############### Authenticaion routes ###############
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Already logged-in?
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!<br>You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template("/auth/register.html", title='Register', form=form)


@app.route('/login',  methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Case sensetive email check (old code)
        #user = User.query.filter_by(email=form.email.data).first()
        user = User.query.filter(User.email.ilike(form.email.data)).first()

        # Successful login?
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            next_page = request.args.get('next')
            flash('Welcome back ' + user.username + '!', 'success')

            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Failed to login.', 'danger')


    return render_template("/auth/login.html", title='Login', form=form)

# Logout
@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out.', 'success')
    return redirect(url_for('home'))
