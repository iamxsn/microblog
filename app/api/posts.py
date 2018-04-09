from flask import jsonify, request, url_for
# from guess_language import guess_language
from app import db
from app.models import Post, User
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request



@bp.route('/posts/<int:id>', methods=['GET'])
@token_auth.login_required
def get_post(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/posts/', methods=['GET'])
@token_auth.login_required
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    data = Post.to_collection_dict(Post.query.order_by(Post.timestamp.desc()), page, per_page, 'api.get_posts')
    return jsonify(data)


@bp.route('/users/<int:id>/posts/', methods=['GET'])
@token_auth.login_required
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    data = Post.to_collection_dict(user.posts.order_by(Post.timestamp.desc()), page, per_page, 'api.get_user_posts', id=id)
    return jsonify(data)


@bp.route('/users/<int:id>/timeline/', methods=['GET'])
@token_auth.login_required
def get_user_timeline(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    data = Post.to_collection_dict(user.followed_posts, page, per_page, 'api.get_user_timeline', id=id)
    return jsonify(data)


@bp.route('/posts/', methods=['POST'])
@token_auth.login_required
def create_post():
    data = request.get_json() or {}
    # language = guess_language(data)
    post = Post()
    post.from_dict(data)
    db.session.add(post)
    db.session.commit()
    response = jsonify(post.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_post', id=post.id)
    return response