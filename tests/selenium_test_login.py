import sys
import os
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proj_models import User
from app import create_app
from config import TestingConfig
from extensions import db
import uuid


class LoginSeleniumTest(unittest.TestCase):

    def setUp(self):
        # Create app context and setup DB
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Clear DB and create fresh schema
        db.drop_all()
        db.create_all()

        # Setup Chrome driver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    password = "testpass123"

    def signup(self, unique_username=unique_username, unique_email=unique_email, password=password):
        self.driver.get("http://localhost:5000/signup")

        driver = self.driver

        # Fill in the form
        driver.find_element(By.ID, "first_name").send_keys("Test")
        driver.find_element(By.ID, "last_name").send_keys("User")
        driver.find_element(By.ID, "email").send_keys(unique_email)
        driver.find_element(By.ID, "phone").send_keys("1234567890")
        driver.find_element(By.ID, "country").send_keys("Australia")
        driver.find_element(By.ID, "dob").send_keys("2000-01-01")
        driver.find_element(By.ID, "username").send_keys(unique_username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "confirm-password").send_keys("testpass123")
        # Submit form
        driver.find_element(By.ID, "signup_button").click()
    
    def test_user_can_login(self, unique_username=unique_username, password=password):
        self.signup()
        self.driver.get("http://localhost:5000/login")

        self.driver.find_element(By.ID, "username").send_keys(unique_username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "login_button").click()

        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Welcome")
        )

        self.assertIn("Welcome", self.driver.page_source)

    def test_user_login_with_invalid_credentials(self):
        self.driver.get("http://localhost:5000/login")

        self.driver.find_element(By.ID, "username").send_keys("wronguser")
        self.driver.find_element(By.ID, "password").send_keys("wrongpass")
        self.driver.find_element(By.ID, "login_button").click()


        flash_container = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "form-errors"))
        )
        assert "invalid username/email or password" in flash_container.text.lower()

    def tearDown(self):
        self.driver.quit()
        self.app_context.pop()
