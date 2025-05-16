# GamblePro Purpose, Design, and Use

## Purpose
The Bookies Website is a comprehensive platform designed for sports enthusiasts and betting enthusiasts to track, analyze, and engage with betting data. It provides users with personalized profiles, public statistics, and a social forum to discuss games and predictions. The platform emphasizes data visualization, user engagement, and a safe, interactive environment for betting.
 
<br>

## Group: 2
### Member Information:
| UWA ID  | Name             | GitHub Username |
|---------|------------------|-----------------|
|23805432 |Callum Breen      |callum-breen     |
|23832656 |Peter Fang        |PFhuahua         |
|24371485 |Caroline Ann      |CrimsonW23       |
|24670672 |Senaya Wimalasena |senayamary       |
<br>

# Launching Instructions
Quickly move to launching instructions for:
- [Windows](#windows)
- [Linux or MacOS](#linuxmacos)

### Windows<br>
#### 1. Launch the Command Prompt<br>

#### 2. Clone the repository:
    git clone https://github.com/CrimsonW23/AgileWebDev3403-BookiesWebsite.git <folder-name>
   - Replace `<folder-name>` with your desired name, or leave it blank and it will be cloned into `AgileWebDev3403-BookiesWebsite.git`<br>
   
#### 3. Navigate to the cloned repository:
    cd <folder-name>
   
#### 4. Create and activate a virtual environment:
    python -m venv venv
    venv\Scripts\activate
  
#### 5. Install dependencies:
    pip install -r requirements.txt

#### 6. Generate the migration script:
    flask db migrate

#### 7. Update the database:
    flask db upgrade

#### 8. Set your secret key (First Launch ONLY):
    echo SECRET_KEY="<secret_key>" >> .env
   - Creates a `.env` file that will contain your secret key
   - Your secret key can be anything
   - This step does not need to be repeated when launching your app again.<br>
   
#### 9. Run the application:
    python app.py

#### 10. Head over to http://127.0.0.1:5000 (or the address your console says the website is hosted at)<br>

<br>

### Linux/MacOS
#### 1. Open your terminal.

#### 2. Clone the repository:
    git clone https://github.com/CrimsonW23/AgileWebDev3403-BookiesWebsite.git <folder-name>
   - Replace `<folder-name>` with your preferred directory name, or omit it to clone into AgileWebDev3403-BookiesWebsite.

#### 3. Navigate into the project folder:<br>
    cd <folder-name>
   
#### 4. Create and activate a virtual environment (recommended):<br>
    python3 -m venv venv
    source venv/bin/activate
   
#### 5. Install the dependencies:<br>
    pip install -r requirements.txt
   
#### 6. Generate the migration script:<br>
    flask db migrate
   
#### 7. Apply the migration to the database:<br>
    flask db upgrade
   
#### 8. Set the secret key environment variable (First Launch ONLY):
    echo SECRET_KEY="<secret_key>" >> .env
   - Creates a `.env` file that will contain your secret key
   - Your secret key can be anything
   - This step does not need to be repeated when launching your app again.<br>

#### 9. Run the application:<br>
    python app.py

#### 10. Open your browser and go to http://127.0.0.1:5000 (or the address shown in your terminal output).<br>

For future development please add the new html pages in the template folder and the css in the static folder.
<br>

# Testing Instructions
#### 1. Launch one instance of the web application.

#### 2. In another terminal, navigate to the folder where you have cloned the repository.

#### 3. Navigate to the `tests` folder

#### 4. To run tests, use the following command:
    python -m unittest <filename>
- **Files for testing:**<br><br>
     Unit Tests:
     - test_forum.py (3 tests)
     - test_friendship.py (3 tests)<br>
     
     Selenium Tests:
     - selenium_test_login.py (2 tests)
     - selenium_test_signup.py (3 tests)
 
#### Important Note
It is recommended to delete and repeat steps 6 and 7 in Launching Instructions to start the tests with a clean database each time.
<br>
