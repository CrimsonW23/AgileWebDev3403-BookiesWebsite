import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proj_models import User
from app import create_app
from config import TestingConfig
from extensions import db

import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import uuid


class SignupSeleniumTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Clear the database and create a new one
        db.drop_all()
        db.create_all()

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get("http://localhost:5000/signup")

    def test_user_can_signup(self):

        unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
        unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"

        driver = self.driver

        # Fill in the form
        driver.find_element(By.ID, "first_name").send_keys("Test")
        driver.find_element(By.ID, "last_name").send_keys("User")
        driver.find_element(By.ID, "email").send_keys(unique_email)
        driver.find_element(By.ID, "phone").send_keys("1234567890")
        driver.find_element(By.ID, "country").send_keys("Australia")
        driver.find_element(By.ID, "dob").send_keys("2000-01-01")
        driver.find_element(By.ID, "username").send_keys(unique_username)
        driver.find_element(By.ID, "password").send_keys("testpass123")
        driver.find_element(By.ID, "confirm-password").send_keys("testpass123")

        # Submit form
        driver.find_element(By.ID, "signup_button").click()

        time.sleep(2)  # wait for page to load

        # Check if redirected or success message appears
        self.assertIn("Welcome", driver.page_source)

    def test_user_signup_with_existing_username(self):
        existing_username = "existinguser"
        unique_email_1 = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
        unique_email_2 = f"testuser_{uuid.uuid4().hex[:8]}@example.com"


        # Create a user with the existing username
        user = User(username=existing_username, email=unique_email_1)
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        driver = self.driver

        # Fill in the form
        driver.find_element(By.ID, "first_name").send_keys("Test")
        driver.find_element(By.ID, "last_name").send_keys("User")
        driver.find_element(By.ID, "email").send_keys(unique_email_2)
        driver.find_element(By.ID, "phone").send_keys("1234567890")
        driver.find_element(By.ID, "country").send_keys("Australia")
        driver.find_element(By.ID, "dob").send_keys("2000-01-01")
        driver.find_element(By.ID, "username").send_keys(existing_username)
        driver.find_element(By.ID, "password").send_keys("testpass123")
        driver.find_element(By.ID, "confirm-password").send_keys("testpass123")

        # Submit form
        driver.find_element(By.ID, "signup_button").click()

        # Wait up to 10 seconds for the flash message container to appear
        flash_container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "form-errors"))
        )

        # Check the text inside the flash container
        assert "username is already taken" in flash_container.text.lower()

    def test_user_signup_with_existing_email(self):
        existing_email = "test@example.com"
        unique_username = f"testuser_{uuid.uuid4().hex[:8]}"

        # Create a user with the existing username
        user = User(username=unique_username, email=existing_email)
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()

        driver = self.driver

        # Fill in the form
        driver.find_element(By.ID, "first_name").send_keys("Test")
        driver.find_element(By.ID, "last_name").send_keys("User")
        driver.find_element(By.ID, "email").send_keys(existing_email)
        driver.find_element(By.ID, "phone").send_keys("1234567890")
        driver.find_element(By.ID, "country").send_keys("Australia")
        driver.find_element(By.ID, "dob").send_keys("2000-01-01")
        driver.find_element(By.ID, "username").send_keys(unique_username)
        driver.find_element(By.ID, "password").send_keys("testpass123")
        driver.find_element(By.ID, "confirm-password").send_keys("testpass123")

        # Submit form
        driver.find_element(By.ID, "signup_button").click()

        # Wait up to 10 seconds for the flash message container to appear
        flash_container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "form-errors"))
        )

        # Check the text inside the flash container
        assert "email is already registered" in flash_container.text.lower()
    
    def tearDown(self):
        self.driver.quit()