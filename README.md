## README Instructions
The creation of the web application should be done in a private GitHub repository that includes a README containing:
- a description of the purpose of the application, explaining its design and use.
- a table with with each row containing the i) UWA ID ii) name and iii) Github user name of the group members.
- instructions for how to launch the application.
- instructions for how to run the tests for the application.
<br>

## Application Purpose, Design, and Use

### Purpose
The Bookies Website is a comprehensive platform designed for sports enthusiasts and betting enthusiasts to track, analyze, and engage with betting data. It provides users with personalized profiles, public statistics, and a social forum to discuss games and predictions. The platform emphasizes data visualization, user engagement, and a safe, interactive environment for betting.

### Purpose


### Purpose


 
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

## Launching Instructions
1. In command prompt or the terminal, activate venv
2. Clone the repository using `git clone https://github.com/CrimsonW23/AgileWebDev3403-BookiesWebsite.git`
3. Install dependencies as listed in the `requirements.txt` file.
4. Run `flask db init` to initialise the database that will store all of your local data.
5. Run `flask db migrate` to generate the migration script.
6. Next, run `flask db upgrade` to update the database.
7. Run `SET SECRET_KEY="<enter secret key>"`, or `EXPORT SECRET_KEY="<enter secret key>"` if you're on Linux.
8. Back in the terminal, `cd` to the directory where you cloned the repository and run `python app.py`
9. Head over to 127.0.0.1 (or the address your console says the website is hosted at).

For future development please add the new html pages in the template folder and the css in the static folder.
<br>

## Testing Instructions
<br>
