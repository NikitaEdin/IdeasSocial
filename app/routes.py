import os
import secrets
import humanize
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateDisplayNameForm, UpdateEmailForm, UpdatePasswordForm
from app.forms import  ProfilePicutreForm, PostForm, CommentForm, EditBioForm
from app.models import User, Post, Comment, Like, Follow
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from flask import jsonify


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



    # Posts per page
    page = request.args.get('page', 1, type=int)
    posts_per_page = 5

    # Fetch all posts
    #posts = Post.query.order_by(Post.date_posted.desc()).all()
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=posts_per_page)

    # Suggested users
    suggested_users = User.get_suggested_users(current_user) if current_user.is_authenticated else []

    for post in posts:
        post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)

    return render_template("home.html", title='Home', current_page='home', 
                           posts=posts, form=form, suggested_users=suggested_users)

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


############################## USER ##############################
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
    page = request.args.get('page', 1, type=int)
    posts_per_page = 5

    # Get user posts (if any)
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=posts_per_page)
    
    for post in posts:
        post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)
    # Stats - total posts
    total_posts = len(Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).all())
    # Stats - Following
    total_following = current_user.following.count()
    # Stats - Followers
    total_followers = current_user.followers.count()
    # Count of posts the current user has liked
    total_liked_posts = Like.query.filter_by(user_id=current_user.id).count()
    
    # Total likes received on all posts by the current user
    total_likes_received = (
        db.session.query(Like)
        .join(Post, Post.id == Like.post_id)
        .filter(Post.user_id == current_user.id)
        .count()
    )



    return render_template("/user/profile.html", removeRightMenu=True, current_page='profile',
                           posts=posts, total_posts=total_posts,
                           total_following=total_following,
                           total_followers=total_followers,
                           total_liked_posts=total_liked_posts,
                           total_likes_received=total_likes_received,
                           title=current_user.username)


# Other user public page
@app.route("/user/<int:id>")
def user_profile(id):
    user = User.query.get_or_404(id)  # Get the user or return a 404 if not found

    # Current user trying to access their own profile?
    if current_user.is_authenticated and current_user.id == user.id:
        return redirect(url_for('profile'))


    # Pagination 
    page = request.args.get('page', 1, type=int)
    posts_per_page = 5

    # Get posts, paginated
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=posts_per_page)
    for post in posts:
        post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)
    # Stats - total posts
    total_posts = len(Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc()).all())
    # Stats - Following
    total_following = user.following.count()
    # Stats - Followers
    total_followers = user.followers.count()
    # Count of posts the current user has liked
    total_liked_posts = Like.query.filter_by(user_id=user.id).count()
    
    # Total likes received on all posts by the current user
    total_likes_received = (
        db.session.query(Like)
        .join(Post, Post.id == Like.post_id)
        .filter(Post.user_id == user.id)
        .count()
    )


    return render_template("/user/user_profile.html", user=user, removeRightMenu=True, 
                           posts=posts, total_posts=total_posts,
                           total_following=total_following,
                           total_followers=total_followers,
                           total_liked_posts=total_liked_posts,
                           total_likes_received=total_likes_received,
                           title=user.username)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_bio():

    bio_form = EditBioForm()
    # Populate the bio (if any)
    if request.method == 'GET':
        bio_form.bio.data = current_user.bio
    
    if bio_form.validate_on_submit():
        current_user.bio = bio_form.bio.data
        db.session.commit()
        flash('Bio updated!', 'success')
        return redirect(url_for('profile'))

    return render_template("/user/edit_bio.html", title='Edit Bio', bio_form=bio_form, removeRightMenu=True)
    

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    # Get user by id
    user_to_follow = User.query.get_or_404(user_id)

    # Prevent users from following themselves
    if user_to_follow == current_user:
        flash("You cannot follow yourself.", 'warning')
        return redirect(url_for('user_profile', user_id=user_id))
    
    # Already following? - Unfollow
    if current_user.is_following(user_to_follow):
        follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user_id).first()
        db.session.delete(follow)
        db.session.commit()
        flash(f"You have unfollowed {user_to_follow.username}.", 'info')
    else:
        # Follow user
        new_follow = Follow(follower_id=current_user.id, followed_id=user_to_follow.id)
        db.session.add(new_follow)
        db.session.commit()
        flash(f"You are now folllwing {user_to_follow.username}.", 'success')

    return redirect(url_for('user_profile', id=user_id))


############################## POSTS ##############################
@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def view_post(post_id):
    # Post post by id or 404
    post = Post.query.get_or_404(post_id)
    
    # Humanise post date
    post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)

    # Pagination 
    page = request.args.get('page', 1, type=int)
    posts_per_page = 5

    # Get post comments with pagination
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).paginate(page=page, per_page=posts_per_page)
    for comment in comments:
        comment.humanized_time = humanize.naturaltime(datetime.utcnow() - comment.date_posted)


    # Handle adding comment
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        # Submited but not authenticated?
        if current_user.is_authenticated:
            comment = Comment(content=comment_form.content.data, user_id=current_user.id, post_id = post.id)
            db.session.add(comment)
            db.session.commit()

            flash('Comment created!', 'success')
            return redirect(url_for('view_post', post_id=post.id))
        else:
            flash('You must be logged-in in order to post comments.', 'danger')
            return redirect(url_for('view_post', post_id=post.id))

    return render_template('/posts/view_post.html', post=post, title=post.title, removeRightMenu=True, comments=comments, comment_form=comment_form)
    post

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
    

    return render_template('/posts/edit_post.html', title='Edit Post', form=form, post=post, removeRightMenu=True)
    

@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash("You are not authorized to delete this post.", "danger")
        return redirect(url_for("/posts/view_post", post_id=post.id))
    
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!", "success")
    return redirect(url_for("home"))


@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if like:
        # User already liked the post; unlike it
        db.session.delete(like)
        liked = False
    else:
        # User has not liked it; add like
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        liked = True

    db.session.commit()
    return jsonify({
        'liked': liked,
        'like_count': post.like_count()
    })


# Feed
@app.route("/feed")
@login_required
def feed():
    # Posts per page
    page = request.args.get('page', 1, type=int)
    posts_per_page = 5

    # Followed users
    followed_users_ids = [follow.followed_id for follow in current_user.following]

    posts = Post.query.filter(Post.user_id.in_(followed_users_ids)).order_by(Post.date_posted.desc()).paginate(page=page, per_page=posts_per_page)

    # Humanise post times
    for post in posts:
        post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)

    # Suggested users
    suggested_users = User.get_suggested_users(current_user) if current_user.is_authenticated else []

    return render_template("feed.html", title='Feed', current_page='feed', posts=posts, suggested_users=suggested_users)


# Logout
@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out.', 'success')
    return redirect(url_for('home'))


########### SEARCH ###########
@app.route('/search', methods=['GET'])
def search():
    # Pagination
    page = request.args.get('page', 1, type=int)  
    per_page = 5

    # Get query from URL
    query = request.args.get('query')

    if query:

        if len(query) < 3 or len(query) > 50:
            flash('Invalid search query. Please enter a valid search term.', 'warning')
            return redirect(url_for('home'))  # Redirect to home if the query is invalid

        # Search query in post titles and contents
        posts = Post.query.filter(
            (Post.title.ilike(f'%{query}%') | (Post.content.ilike(f'%{query}%')))
        ).order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page)
    else:
        posts = []

    return render_template('search_results.html', 
                           title='Search',
                           posts=posts, query=query)



############################## ERRORS OR COMMON ##############################
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