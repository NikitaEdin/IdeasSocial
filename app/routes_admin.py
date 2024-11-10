# routes_admin.py
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
import humanize
from app import app, db
from app.decorators import admin_required
from app.forms import EditUserForm
from app.models import Post, User, Comment, Like
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Example route within the admin Blueprint
@admin_bp.route('/')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    total_likes = Like.query.count()

    # Recent Posts
    recent_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()
    # Add humanized time to posts
    for post in recent_posts:
        post.humanized_time = humanize.naturaltime(datetime.now() - post.date_posted)

    # Recent Comments
    recent_comments = Comment.query.join(User).join(Post).order_by(Comment.date_posted.desc()).limit(5).all()
    # Add humanized time to comments
    for comment in recent_comments:
        comment.humanized_time = humanize.naturaltime(datetime.now() - comment.date_posted)


    return render_template('/admin/admin_dashboard.html', current_page = 'dashboard', title='Admin Dashboard',
                           total_users=total_users,
                           total_posts=total_posts,
                           total_comments=total_comments,
                           total_likes=total_likes,
                           recent_posts=recent_posts,
                           recent_comments=recent_comments)

@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    posts_per_page = 10

    # Fetch users
    users = User.query.paginate(page=page, per_page=posts_per_page)

    return render_template('/admin/admin_users.html' ,current_page = 'users', title='Admin Users',
                           users=users)


@admin_bp.route('/user/<int:user_id>/edit', methods=['GET','POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    form = EditUserForm(obj=user) # Prepopulate the fields with user data

    if form.validate_on_submit():
        # Update user
        user.username = form.username.data
        user.email = form.email.data
        user.displayname = form.displayname.data
        user.bio = form.bio.data

         # Check if a new password is provided
        if form.password.data:
            user.password = user.set_password(form.password.data)

        db.session.commit()
        flash(f"User '{user.username}' was updated successfully.", "success")
        return redirect(url_for('admin.users'))
    
    return render_template('/admin/edit_user.html', form=form, user=user)
        


# Create the Blueprint for admin routes
# NOTE: keep this at the very bottom
app.register_blueprint(admin_bp)


