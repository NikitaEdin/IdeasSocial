from flask import Blueprint, abort, jsonify
from .models import Like, Post, User, Comment

api_bp = Blueprint('api', __name__)

# API - Get all users
@api_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'displayname': user.displayname,
            'bio': user.bio,
            'image_file': user.image_file
        }
        for user in users
    ]
    return jsonify(user_list)


# API - Get a specific user by ID
@api_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    
    if user is None:
        abort(404, description="User not found")
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'displayname': user.displayname,
        'bio': user.bio,
        'image_file': user.image_file
    }
    
    return jsonify(user_data)


# API - Get all posts
@api_bp.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    post_list = [
        {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'date_posted': post.date_posted,
            'user_id': post.user_id,
            'total_likes': Like.query.filter_by(post_id=post.id).count()
            
        }
        for post in posts
    ]
    return jsonify(post_list)

@api_bp.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.query.get(id)
    
    if post is None:
        abort(404, description="Post not found")
    
    total_likes = Like.query.filter_by(post_id=post.id).count()

    post_data = {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'date_posted': post.date_posted,
        'user_id': post.user_id,
        'total_likes': total_likes
    }
    
    return jsonify(post_data)



@api_bp.route('/posts/<int:id>/comments', methods=['GET'])
def get_comments(id):
    post = Post.query.get(id)
    
    if post is None:
        abort(404, description="Post not found")
    
    # Get all comments from this post
    comments = Comment.query.filter_by(post_id=id).all()
    comments_data = []
    for comment in comments:
        comment_data = {
            'id': comment.id,
            'content': comment.content,
            'date_posted': comment.date_posted.isoformat(),
            'author': get_user_by_id(comment.user_id)
        }
        comments_data.append(comment_data)
    
    return jsonify(comments_data)


def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if user:
        return {
            'id': user.id,
            'username': user.username,
            'displayname': user.displayname
        }
    else:
        return {"error": "User not found"}