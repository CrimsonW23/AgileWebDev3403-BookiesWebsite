import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proj_models import FriendRequest, Friendship, User
from extensions import db
from app import app
from datetime import datetime, date
from sqlalchemy.orm import sessionmaker

import json

import unittest

class ForumTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        app.testing = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.app_context():
            Friendship.query.delete()
            User.query.delete()
            FriendRequest.query.delete()
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
    
    def test_no_friends(self):
        self.login()

        #Access the /friends page
        response = self.app.get('/friends', follow_redirects=True)

        # Assert correct response
        self.assertEqual(response.status_code, 200)

        data = response.data.decode()

        # Assert that the friends list is empty
        self.assertNotIn('<ul class="friends-list">', data)

    def test_friends_list(self):
        self.login()
        
        friend = User(id = 2,
                      username = 'frienduser',
                      email = "test@gmail.com",
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
        
        friend.set_password('testpassword')

        with app.app_context():
            db.session.add(friend)
            db.session.commit()
                
            # Get the engine bound to 'friends'
            engine_friends = db.get_engine(app, bind='friends')

            # Create a new Session bound to the 'friends' engine
            SessionFriends = sessionmaker(bind=engine_friends)
            friends_session = SessionFriends()

            # Add friendship
            friends_session.add(Friendship(user_id=self.user_id, friend_id=friend.id))
            friends_session.commit()

        # Access the /friends page
        response = self.app.get("/friends")

        # Assert correct response and that the friend appears
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'frienduser', response.data)  # Confirm friend username appears

    def test_friend_request(self):
        # Create sender and receiver
        sender = User(id=2,
                    username='sender',
                    email="sender@example.com",
                    password="testpassword",
                    first_name="Sender",
                    last_name="User",
                    phone="1234567890",
                    country="Australia",
                    dob=date(2000, 1, 1),
                    currency=100.0,
                    date_joined=datetime.now().date(),
                    active=True,
                    profile_pic="default.png")
        sender.set_password('testpassword')

        with app.app_context():
            db.session.add(sender)
            db.session.commit()

            # Save sender's ID before the context closes
            sender_id = sender.id

            # Create the friend request
            fr = FriendRequest(from_id=sender_id, to_id=self.user_id, status="pending")
            db.session.add(fr)
            db.session.commit()
            request_id = fr.id


        # Log in as the receiver (self.user)
        self.login()

        # Accept the friend request
        response = self.app.post(f"/friend-request/{request_id}/accept", follow_redirects=True)

        # Check the redirect and friendship creation
        self.assertEqual(response.status_code, 200)

        with app.app_context():
            # Reload the friend request and check if it was accepted
            updated_fr = FriendRequest.query.get(request_id)
            self.assertEqual(updated_fr.status, "accepted")

            # Check that reciprocal friendships were created
            engine_friends = db.get_engine(app, bind='friends')
            SessionFriends = sessionmaker(bind=engine_friends)
            friends_session = SessionFriends()

            f1 = friends_session.query(Friendship).filter_by(user_id=self.user_id, friend_id=sender_id).first()
            f2 = friends_session.query(Friendship).filter_by(user_id=sender_id, friend_id=self.user_id).first()

            self.assertIsNotNone(f1)
            self.assertIsNotNone(f2)