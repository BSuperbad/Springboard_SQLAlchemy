# python3 -m unittest test_flask

from unittest import TestCase

from app import app
from models import db, User, Post

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class UserTestCase(TestCase):
    """Tests users table"""

    def setUp(self):
        """Add sample user"""

        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()

        db.drop_all()
        db.create_all()

        user = User(first_name="Test", last_name="User")
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id
        self.user = user

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()
        db.session.remove()
        self.ctx.pop()

    def test_home_page(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test", html)

    def test_add_new_user(self):
        with app.test_client() as client:
            data = {
                'first_name': 'John',
                'last_name': 'Doe',
                'image_url': ''
            }
            response = client.post(
                '/users/new', data=data, follow_redirects=False)

            self.assertEqual(response.status_code, 302)

            redirected_response = client.get(
                response.location, follow_redirects=True)

            self.assertEqual(redirected_response.status_code, 200)

            user = User.query.filter_by(
                first_name='John', last_name='Doe').first()
            self.assertIsNotNone(user)

            self.assertIsNotNone(response.location)
            self.assertIn(f'/users/{user.id}', response.location)

    def test_delete_user(self):
        test_user = User(first_name='John', last_name='Doe', image_url=None)
        db.session.add(test_user)
        db.session.commit()

        with app.test_client() as client:
            response = client.post(
                f'/users/{test_user.id}/delete', follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            deleted_user = User.query.get(test_user.id)
            self.assertIsNone(deleted_user)

    def test_edit_user_form(self):
        test_user = User(first_name='John', last_name='Doe', image_url=None)
        db.session.add(test_user)
        db.session.commit()
        with app.test_client() as client:
            response = client.get(f'/users/{test_user.id}/edit')

            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)

            self.assertIn('John', html)
            self.assertIn('Doe', html)


class PostTestCase(TestCase):
    """Tests posts table"""

    def setUp(self):
        """Add sample post"""

        Post.query.delete()

        post = Post(title="Test", content="Post content")
        db.session.add(post)
        db.session.commit()

        self.post_id = post.id
        self.post = post

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_show_post(self):
        user = User(first_name='John', last_name='Doe')
        post = Post(title='Test Post', content='Test Content', user=user)
        db.session.add(user)
        db.session.add(post)
        db.session.commit()
        with app.test_client() as client:

            response = client.get(f'/users/{user.id}/posts/{post.id}')
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Test Post', html)

    def test_show_new_post_form(self):
        with app.test_client() as client:
            response = client.get('/users/1/posts/new')
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Add New Post', html)

    def test_delete_post(self):
        post = Post(title='Test Post', content='Here is my test post!')
        db.session.add(post)
        db.session.commit()

        with app.test_client() as client:
            response = client.post(
                f'/posts/{post.id}/delete', follow_redirects=True)

            deleted_post = Post.query.get(post.id)
            self.assertIsNone(deleted_post)
