from flask import jsonify, request, url_for
from app import db
from app.models import User
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)


@bp.route('/users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followers, page, per_page,
                                   'api.get_followers', id=id)
    return jsonify(data)


@bp.route('/users/<int:id>/followed', methods=['GET'])
@token_auth.login_required
def get_followed(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followed, page, per_page,
                                   'api.get_followed', id=id)
    return jsonify(data)


@bp.route('/users/<int:id>/is_following/<username>', methods=['GET'])
@token_auth.login_required
def is_following(id, username):
    current_user = User.query.get_or_404(id)
    user = User.query.filter_by(username=username).first()
    is_following = current_user.is_following(user)
    return jsonify({'is_following': is_following})

@bp.route('/users/<int:id>/follow/<username>', methods=['PUT'])
@token_auth.login_required
def follow(id, username):
    # current_user = User.query.get_or_404(id)
    # data = request.get_json() or {}
    current_user = User.query.get_or_404(id)
    user = User.query.filter_by(username=username).first()
    current_user.follow(user)
    db.session.commit()
    return '', 204


@bp.route('/users/<int:id>/unfollow/<username>', methods=['PUT'])
@token_auth.login_required
def unfollow(id, username):
    # current_user = User.query.get_or_404(id)
    # data = request.get_json() or {}
    current_user = User.query.get_or_404(id)
    user = User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    db.session.commit()
    return '', 204


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('该用户名已被使用')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('该邮箱已被注册')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('该用户名已被使用')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('该邮箱已被注册')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())
