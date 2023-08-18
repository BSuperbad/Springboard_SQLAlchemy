# pip3 install psycopg2-binary
# pip3 install flask-sqlalchemy

"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag

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


@app.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template("home.html", posts=posts)

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


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Shows individual post page"""
    post = Post.query.get_or_404(post_id)
    return render_template('posts/show.html', post=post, user=post.user)


@app.route('/users/<int:user_id>/posts/new', methods=['GET'])
def show_new_post_form(user_id):
    """Shows new post form page"""
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('posts/new.html', user=user, tags=tags)


@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def add_new_post(user_id):
    """Adds new post to database and lists under current user"""
    user = User.query.get_or_404(user_id)
    tag_ids = [int(num) for num in request.form.getlist('tags')]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    new_post = Post(title=request.form["title"],
                    content=request.form["content"], user=user, tags=tags)

    db.session.add(new_post)
    db.session.commit()
    return redirect(f'/users/{user_id}')


@app.route('/posts/<int:post_id>/edit')
def edit_post_form(post_id):
    """Shows edit post form"""
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()

    return render_template('posts/edit.html', post=post, tags=tags)


@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def edit_post(post_id):
    """Adds edited post to database connected to user and takes you to their user page"""
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    tag_ids = [int(num) for num in request.form.getlist('tags')]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    db.session.add(post)
    db.session.commit()

    return redirect(f'/users/{post.user_code}')


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Deletes post from database"""
    post_del = Post.query.get_or_404(post_id)
    db.session.delete(post_del)
    db.session.commit()
    return redirect(f'/users/{post_del.user_code}')

# TAG ROUTES


@app.route('/tags')
def show_tags():
    """Shows Tag List"""
    tags = Tag.query.all()
    return render_template('tags/base.html', tags=tags)


@app.route('/tags/new', methods=['GET'])
def show_new_tag_form():
    """Shows new user form page"""
    posts = Post.query.all()
    return render_template('tags/add-tag.html', posts=posts)


@app.route('/tags/new', methods=['POST'])
def add_new_tag():
    """Adds new tag to database and takes you to the tag list"""

    new_tag = Tag(name=request.form['tag_name'])
    post_ids = [int(num) for num in request.form.getlist('posts')]
    new_tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(new_tag)
    db.session.commit()

    return redirect(f'/tags/{new_tag.id}')


@app.route('/tags/<int:tag_id>')
def show_tag_info(tag_id):
    """Shows all the posts associated with said tag"""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/details.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit')
def edit_tag_form(tag_id):
    """Shows edit tag form"""
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tags/edit.html', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def edit_tag(tag_id):
    """Adds edited tag to database connected to post and takes you back to the tag list"""
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form["tag_name"]
    post_ids = [int(num) for num in request.form.getlist('posts')]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()

    return redirect('/tags')


@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    """Deletes tag from database"""
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(f'/tags/{tag.tag_id}')
