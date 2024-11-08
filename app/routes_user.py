import humanize
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.forms import UpdateDisplayNameForm, UpdateEmailForm, UpdatePasswordForm
from app.forms import  ProfilePicutreForm, EditBioForm
from app.models import User, Post, Like, Follow
from flask_login import current_user, login_required
from datetime import datetime

# Global/static variables
POSTS_PER_PAGE = 5

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
    posts_per_page = POSTS_PER_PAGE

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
    posts_per_page = POSTS_PER_PAGE

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

