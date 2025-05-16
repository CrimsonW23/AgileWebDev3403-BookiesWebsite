import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proj_models import User, Post, Reply
from extensions import db
from app import app
from datetime import datetime, date
import json

import unittest


class ForumTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        app.testing = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.app_context():
            Post.query.delete()
            User.query.delete()
            Reply.query.delete()
            db.session.commit()

        self.user = User(id = 1,
                        username = 'testuser',
                        email = "test@example.com",
                        password = "testpassword",
                        first_name = "Test",
                        last_name = "User",
                        phone = "1234567890",
                        country = "Australia",
                        dob = date(2000, 1, 1),
                        currency = 100.0,
                        date_joined = datetime.now().date(),
                        active = True,
                        profile_pic = "default.png",)
        
        
        self.user.set_password('testpassword')
        self.user_id = self.user.id
        
        with app.app_context():
            db.session.add(self.user)
            db.session.commit()

            
    def login(self, username='testuser', password='testpassword'):
        response = self.app.post('/login', data={
            'username': username,
            'password': password
        }, content_type='application/x-www-form-urlencoded')
        data = json.loads(response.data)
        print("Login response:", response.data.decode())
        assert data['success'] == True, "Login failed in test helper"
        return response

    # Tests the /forum route
    def test_forum_empty(self):
        # Login user first (assuming login helper method exists)
        self.login()

        # Ensure no posts exist in DB
        with app.app_context():
            Post.query.delete()
            db.session.commit()

        # Request /forum with no category param (defaults to 'all')
        response = self.app.get('/forum')

        self.assertEqual(response.status_code, 200)

        # Check if the response contains the expected HTML elements
        self.assertIn(b'<option value="all" selected>', response.data)

        # Check if the response contains the expected HTML elements
        self.assertNotIn(b'<td><a href=', response.data)

    # Tests the Post model and functionality
    def test_forum_post(self):
        # Login user first (assuming login helper method exists)
        self.login()

        with app.app_context():
            user = User.query.get(self.user_id)  # re-load user bound to current session

            Post.query.delete()
            
            post = Post(
                title='Test Post',
                body='This is a test post.',
                category='General',
                timestamp=datetime.now().replace(second=0, microsecond=0),
                author_id=user.id,
                privacy='public'
            )
            
            db.session.add(post)
            db.session.commit()

        # Request /forum with no category param (defaults to 'all')
        response = self.app.get('/forum')

        self.assertEqual(response.status_code, 200)

        # Check if the response contains the expected HTML elements
        self.assertIn(b'<option value="all" selected>', response.data)

        # Check if the response contains the expected HTML elements
        self.assertIn(b'<td><a href=', response.data)

    
    # Tests the Reply model and functionality
    def test_post_reply(self):
        # Login user first (assuming login helper method exists)
        self.login()

        with app.app_context():
            user = User.query.get(self.user_id)

            Post.query.delete()
            Reply.query.delete()

            post = Post(
                title='Test Post',
                body='This is a test post.',
                category='General',
                timestamp=datetime.now().replace(second=0, microsecond=0),
                author_id=user.id,
                privacy='public'
            )
            
            db.session.add(post)

            reply = Reply(
                body='This is a test reply.',
                timestamp=datetime.now().replace(second=0, microsecond=0),
                author_id=user.id,
                post_id=1
            )

            db.session.add(reply)
            db.session.commit()

        response = self.app.get('/posts/1')

        self.assertEqual(response.status_code, 200)

        data = response.data.decode()

        # Check recent reply has recent-reply class
        self.assertIn('<div class="recent-reply">', data)