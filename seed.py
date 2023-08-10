"""Seed file to make sample data for db"""

from models import User, Post, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

jason = User(first_name='Jason', last_name='Whistles')
test = User(first_name='Test', last_name='Person',
            image_url='https://st.depositphotos.com/1909187/2819/i/600/depositphotos_28193927-stock-photo-blank-posture-front-blue-medical.jpg')
brianne = User(first_name='Brianne', last_name='Superbad',
               image_url='https://images.unsplash.com/photo-1632165258904-21ca36a01ee0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8cHVnfGVufDB8fDB8fHww&w=1000&q=80')
test2 = User(first_name='Tester', last_name='Account')

j_p1 = Post(title="My First Post",
            content="Hi, this is my first post!", user=jason)
j_p2 = Post(title="My Second Post",
            content="Hi, this is my second post!", user=jason)
t_p1 = Post(title="Test Post", content="Hi, this is my first post!", user=test)
t_p2 = Post(title="Second Test Post",
            content="Hi, this is my second post!", user=test)
b_p1 = Post(title="Hello", content="Howdy!", user=brianne)
b_p2 = Post(title="Hello Again",
            content="Hi, this is my second post!", user=brianne)
b_p3 = Post(title="Thoughts and Prayers",
            content="Hi, this is my second post!", user=brianne)
t2_p1 = Post(title="Test 2 Post 1", content="sdfsdfsdgsdg", user=test2)
t2_p2 = Post(title="Test 2 Post 2", content="AHHHHHHH!", user=test2)
t2_p3 = Post(title="Test 2 Post 3", content="Better now!", user=test2)

db.session.add_all([jason, test, brianne, test2])

db.session.commit()

db.session.add_all([j_p1, j_p2, t_p1, t_p2, b_p1,
                   b_p2, b_p3, t2_p1, t2_p2, t2_p3])

db.session.commit()
