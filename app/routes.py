import humanize
from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import PostForm
from app.models import User, Post
from flask_login import current_user, login_required
from datetime import datetime

# Global/static variables
POSTS_PER_PAGE = 5

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
    posts_per_page = POSTS_PER_PAGE

    # Fetch all posts
    #posts = Post.query.order_by(Post.date_posted.desc()).all()
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=posts_per_page)

    # Suggested users
    suggested_users = User.get_suggested_users(current_user) if current_user.is_authenticated else []

    for post in posts:
        post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)

    return render_template("home.html", title='Home', current_page='home', 
                           posts=posts, form=form, suggested_users=suggested_users)



# Feed
@app.route("/feed")
@login_required
def feed():
    # Posts per page
    page = request.args.get('page', 1, type=int)
    posts_per_page = POSTS_PER_PAGE 

    # Followed users
    followed_users_ids = [follow.followed_id for follow in current_user.following]

    posts = Post.query.filter(Post.user_id.in_(followed_users_ids)).order_by(Post.date_posted.desc()).paginate(page=page, per_page=posts_per_page)

    # Humanise post times
    for post in posts:
        post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)

    # Suggested users
    suggested_users = User.get_suggested_users(current_user) if current_user.is_authenticated else []

    return render_template("feed.html", title='Feed', current_page='feed', posts=posts, suggested_users=suggested_users)



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


        # Humanised time
        for post in posts:
            post.humanized_time = humanize.naturaltime(datetime.utcnow() - post.date_posted)
    else:
        posts = []

    return render_template('search_results.html', 
                           title='Search',
                           posts=posts, query=query)



############################## ERRORS OR COMMON ##############################
@app.errorhandler(404)
def not_found(error):
    return render_template('/errors/404.html'), 404 

@app.errorhandler(403)
def forbidden(error):
    return render_template('/errors/403.html'), 403


@app.route('/coming-soon')
def coming_soon():
    return render_template('/errors/coming_soon.html') 



########## INFORMATIONAL PAGES ###########
@app.route("/privacy-policy")
def privacy():
    return render_template('/info/privacy_policy.html', title='Privacy Policy') 

@app.route("/terms-of-service")
def terms_of_service():
    return render_template('/info/terms_of_service.html', title='Terms of Service') 

@app.route("/contact-us")
def contact_us():
    return render_template('/info/contact_us.html', title='Contact') 