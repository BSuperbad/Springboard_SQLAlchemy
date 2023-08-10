# pip3 install psycopg2-binary
# pip3 install flask-sqlalchemy

"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.app_context().push()

app.config['SECRET_KEY'] = 'secret'
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

# USER ROUTES


@app.route('/users')
def home_page():
    """Shows home page"""
    users = User.query.all()
    return render_template('users/base.html', users=users)


@app.route('/users/new', methods=['GET'])
def show_new_user_form():
    """Shows new user form page"""
    return render_template('users/add-user.html')


@app.route('/users/new', methods=['POST'])
def add_new_user():
    """Adds new user to database and takes you to their page"""
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"] or None

    new_user = User(first_name=first_name,
                    last_name=last_name, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()

    return redirect(f'/users/{new_user.id}')


@app.route('/users/<int:user_id>')
def show_user_info(user_id):
    """Shows individual user page"""
    found_user = User.query.get_or_404(user_id)
    return render_template('users/details.html', user=found_user)


@app.route('/users/<int:user_id>/edit')
def edit_user_form(user_id):
    """Shows edit user form"""
    found_user = User.query.get_or_404(user_id)
    return render_template('users/edit-user.html', user=found_user)


@app.route('/users/<int:user_id>/edit', methods=['POST'])
def edit_user(user_id):
    """Adds new user to database and takes you to their page"""
    edited_user = User.query.get_or_404(user_id)
    edited_user.first_name = request.form["first_name"]
    edited_user.last_name = request.form["last_name"]
    edited_user.image_url = request.form["image_url"] or None

    db.session.add(edited_user)
    db.session.commit()

    return redirect('/users')


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Deletes user from database"""
    user_del = User.query.get_or_404(user_id)
    if user_del:
        Post.query.filter_by(user_code=user_del.id).delete()
        db.session.delete(user_del)
        db.session.commit()
        return 'User and associated posts deleted successfully'
    else:
        return 'User not found'

# POST ROUTES


@app.route('/users/<int:user_id>/posts/<int:post_id>')
def show_post(user_id, post_id):
    """Shows individual post page"""
    user = User.query.get_or_404(user_id)
    post = Post.query.get_or_404(post_id)
    return render_template('posts/show.html', user=user, post=post)


@app.route('/users/<int:user_id>/posts/new', methods=['GET'])
def show_new_post_form(user_id):
    """Shows new post form page"""
    user = User.query.get_or_404(user_id)
    return render_template('posts/new.html', user=user)


@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def add_new_post(user_id):
    """Adds new post to database and lists under current user"""
    user = User.query.get_or_404(user_id)

    new_post = Post(title=request.form["title"],
                    content=request.form["content"], user=user)

    db.session.add(new_post)
    db.session.commit()
    return redirect(f'/users/{user_id}')


@app.route('/posts/<int:post_id>/edit')
def edit_post_form(post_id):
    """Shows edit post form"""
    post = Post.query.get_or_404(post_id)

    return render_template('posts/edit.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def edit_post(post_id):
    """Adds edited post to database connected to user and takes you to their user page"""
    edited_post = Post.query.get_or_404(post_id)

    edited_post.title = request.form["title"]
    edited_post.content = request.form["content"]

    db.session.add(edited_post)
    db.session.commit()

    return redirect(f'/users/{edited_post.user_code}')


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Deletes post from database"""
    post_del = Post.query.get_or_404(post_id)
    db.session.delete(post_del)
    db.session.commit()
    return redirect(f'/users/{post_del.user_code}')
