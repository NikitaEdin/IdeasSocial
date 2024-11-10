import humanize
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.decorators import admin_required
from app.forms import  PostForm, CommentForm
from app.models import Post, Comment, Like
from flask_login import current_user, login_required
from datetime import datetime
from flask import jsonify

# Global/static variables
POSTS_PER_PAGE = 5


############################## POSTS ##############################
@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def view_post(post_id):
    # Post post by id or 404
    post = Post.query.get_or_404(post_id)
    
    # Humanise post date
    post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)

    # Pagination 
    page = request.args.get('page', 1, type=int)
    posts_per_page = POSTS_PER_PAGE

    # Get post comments with pagination
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).paginate(page=page, per_page=posts_per_page)
    for comment in comments:
        comment.humanized_time = humanize.naturaltime(datetime.utcnow() - comment.date_posted)


    # Handle adding comment
    comment_form = CommentForm()
    if comment_form.validate_on_submit() and 'submit_comment' in request.form:
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
    if post.author != current_user and not current_user.is_admin():
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
    if post.author != current_user and not current_user.is_admin():
        flash("You are not authorized to delete this post.", "danger")
        return redirect(url_for("/posts/view_post", post_id=post.id))
    
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!", "success")
    return redirect(url_for("home"))


@app.route("/comment/<int:comment_id>/delete", methods=["POST"])
@admin_required
def delete_comment(comment_id):
    # Get comment by id
    comment = Comment.query.get_or_404(comment_id)
    # Delete found comment
    db.session.delete(comment)
    db.session.commit()
    # Display flash message
    flash('The comment has been deleted successfully.', 'success')
    # Redirect back to post
    return redirect(url_for('view_post', post_id=comment.post_id))
    



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

