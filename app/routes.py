import os
import secrets
import humanize
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateDisplayNameForm, UpdateEmailForm, UpdatePasswordForm, ProfilePicutreForm, PostForm
from app.models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


# Main homepage
@app.route("/", methods=['GET', 'POST'])
@app.route("/home",  methods=['GET', 'POST'])
def home():
    form = PostForm()

    # Check if form is submitted and valid
    if form.validate_on_submit(): 
        # Check if user is authenticated
        if not current_user.is_authenticated:
            flash('You must be logged in to post a message.', 'warning')
            return redirect(url_for('login'))

        # Create post
        new_post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))




    # Fetch all posts
    posts = Post.query.order_by(Post.date_posted.desc()).all()

    for post in posts:
        post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)

    return render_template("home.html", title='Home', current_page='home', posts=posts, form=form)


# Authenticaion routes#
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
        user = User.query.filter_by(email=form.email.data).first()
        # Successful login?
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            next_page = request.args.get('next')
            flash('Welcome back ' + user.username + '!', 'success')

            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Failed to login.', 'danger')


    return render_template("/auth/login.html", title='Login', form=form)


############### USER  ###############
# Settings
@app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    image_file = url_for('static', filename='users/DefaultUser.png')
    if current_user.image_file:
        image_file = url_for('static', filename='profile_images/' + current_user.image_file)


    # Init forms
    display_name_form = UpdateDisplayNameForm()
    email_form = UpdateEmailForm()
    password_form = UpdatePasswordForm()
    profile_picture_form = ProfilePicutreForm()
    active_form = None


    # Handle profile pictures
    if profile_picture_form.validate_on_submit() and 'submit_profile_picture' in request.form:
        file = profile_picture_form.profile_picture.data
        if file:
            success = current_user.save_picture(file)
            if success:
                flash('Profile picture updated!', 'success')
            else:
                flash("There was an error updating your profile picture. Please try again.", 'danger')
            
            return redirect(url_for('settings'))
        else:
            flash('Something went wrong with handing the file.', 'danger')
            return redirect(url_for('settings'))
    elif 'submit_profile_picture' in request.form:
        active_form = 'profile_picture'



    # Handle display name update
    if display_name_form.validate_on_submit() and 'submit_display_name' in request.form:
        current_user.displayname = display_name_form.display_name.data
        db.session.commit()
        flash('Display name updated successfully!', 'success')
        return redirect(url_for('settings'))
    elif 'submit_display_name' in request.form:
        active_form = 'displayname'
    
    # Handle email update
    if email_form.validate_on_submit() and 'submit_email' in request.form:
        current_user.email = email_form.email.data
        db.session.commit()
        flash('Email updated successfully!', 'success')
        return redirect(url_for('settings'))
    elif 'submit_email' in request.form:
        active_form = 'email'
    
    # Handle password update
    if 'submit_password' in request.form and password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('settings'))
        else:
            flash('Current password is incorrect', 'danger')
    elif 'submit_password' in request.form:
        active_form = 'password'


    return render_template("/user/settings.html", title='Settings', removeRightMenu=True, 
                           current_page='settings', image_file=image_file,
                           display_name_form=display_name_form,
                           email_form = email_form,
                           password_form = password_form,
                           profile_picture_form=profile_picture_form,
                           active_form = active_form)

# Current_User profile
@app.route("/profile")
@login_required
def profile():
    # Get user posts (if any)
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).all()
    for post in posts:
        post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)
    # Stats - total posts
    total_posts = len(posts)
    # Stats - Following
    total_following = 0
    # Stats - Followers
    total_followers = 0



    return render_template("/user/profile.html", removeRightMenu=True, current_page='profile',
                           posts=posts, total_posts=total_posts,
                           total_following=total_following,
                           total_followers=total_followers,
                           title=current_user.username)


# Other user public page
@app.route("/user/<int:id>")
def user_profile(id):
    user = User.query.get_or_404(id)  # Get the user or return a 404 if not found

    # Current user trying to access their own profile?
    if current_user.is_authenticated and current_user.id == user.id:
        return redirect(url_for('profile'))

    posts = Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc()).all()
    for post in posts:
        post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)
    # Stats - total posts
    total_posts = len(posts)
    # Stats - Following
    total_following = 0
    # Stats - Followers
    total_followers = 0


    return render_template("/user/user_profile.html", user=user, 
                           posts=posts, total_posts=total_posts,
                           total_following=total_following,
                           total_followers=total_followers,
                           title=user.username)


########## POSTS ###############
@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.asc()).all() 

    return render_template('view_post.html', post=post, title=post.title, removeRightMenu=True, comments=comments)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    # User owns the post
    if post.author != current_user:
        flash("You do not have permission to edit this post.", "danger")
        return redirect(url_for('home'))
    
    form = PostForm()

    # Populate the form with current post data
    if request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    # Handle form submission
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('view_post', post_id=post.id))
    

    return render_template('edit_post.html', title='Edit Post', form=form, post=post, removeRightMenu=True)
    

@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash("You are not authorized to delete this post.", "danger")
        return redirect(url_for("view_post", post_id=post.id))
    
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!", "success")
    return redirect(url_for("home"))



# Feed
@app.route("/feed")
@login_required
def feed():
    return render_template("/errors/coming_soon.html", removeRightMenu=True, current_page='feed')


# Logout
@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out.', 'success')
    return redirect(url_for('home'))




########### ERRORS OR COMMON ###########
@app.errorhandler(404)
def not_found(error):
    return render_template('/errors/404.html'), 404 


@app.route('/coming-soon')
def coming_soon():
    return render_template('/errors/coming_soon.html') 



########## INFORMATIONAL PAGES ###########
@app.route("/privacy-policy")
def privacy():
    abort(404)

@app.route("/terms-of-service")
def terms_of_service():
    abort(404)

@app.route("/contact-us")
def contact_us():
    abort(404)