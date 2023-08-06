# pip3 install psycopg2-binary
# pip3 install flask-sqlalchemy

"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

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
    db.session.delete(user_del)
    db.session.commit()
    return redirect('/users')
