# 449-Project-2

# Team members:
1. Ashley Thorlin
2. Harshith Harijeevan
3. Jiu Lin
4. Brijesh Prajapati

## Documentation
Procfile and .env from https://github.com/ProfAvery/cpsc449/tree/master/quart/hello

# Introduction
The goal is to Design endpoints for an application similar to Wordle. It will allow user to play more than one game in a day unlike the orignal wordle. The user will get overall six chances to guess the correct word. The guesses will be matched against the secret word to determine if it is correct or incorrect. If it's correct, the game will stop and if it is incorrect the user will get their remaining chances to guess.
The implementation of API is done in Python using the Quart framework and some ancillary tools like Foreman and sqlite3. The project also requires to create relational database schemas for the API implementation.
By splitting the service into games and users micro-service, we are now utilising seperate SQLite relational databases, such that the services run independently. This entails to denormalization, wherein we are having duplicate information in the form of user tables(username) in both databases. Hence in the Procfile, we have to run both the microservices.
To authenticate all the endpoints instead of just the user endpoint, we will be using a reverse proxy, namely nginx web server. THe nginx auth_request module creates a sub request that allows authentication via an external service.

# Project 2
## How to initialize databases
To initialize the sqlite database, navigate to the project directory using a terminal and then type in `./bin/init.sh` or `sh ./bin/init.sh`.

## How to configure Nginx
To configure nginx, we should create the configuration file inside etc/nginx/sites-enabled from the root directory. In this case we have the tutorial file which is in this repository, that needs to be moved to the above path. Once that is done, start the nginx web service using the command - "sudo service nginx restart". 

## How to start services
To start the web service, run the command "foreman start -m users=1,games=3" which will run one user service and three game services. Here, the -m is used instead of the --formation switch. The changes for load balancer requirement has been done in the tutorials file as mentioned above. No Authentication is required for the signin and the register endpoints.


# Project 1
## How to use endpoints
  HTTP verbs | endpoints | Action 

- To register a new user: `http POST http://tuffix-vm/auth/register username={user} password={pass}`
example - `http POST http://tuffix-vm/auth/register username="jolin" password="007"`
- To sign in: `http -a {username}:{password} http://tuffix-vm/auth/signin`
- To create a game: `http -a {username}:{password} POST http://tuffix-vm/games/create username={username}`
example - `http -a "jolin":"007" POST http://tuffix-vm/games/create username="jolin"`
- To make a guess: `http -a {username}:{password} POST http://tuffix-vm/games/{gameid} guess={guess}`  
example - `http -a "jolin":"007" POST http://tuffix-vm/games/5 guess="start"`
- To list in-progress games : `http -a {username}:{password} GET http://tuffix-vm/users/{username}`
example - `http -a "jolin":"007" GET http://tuffix-vm/users/jolin`
- To retrieve game state : `http -a {username}:{password} GET http://tuffix-vm/games/{gameid}`
example - `http -a "jolin":"007" GET http://tuffix-vm/games/5`

Furthermore, you can view these endpoints in Quart Schema Documentation form when the server is running by navigating to `http://tuffix-vm/docs` in a web browser!

## Features:
 Creating a RESTful API that perform the following functionalities:

 - User registration
 - User HTTP Basic Authentication
 - User Signin(Authentication with password hashing)
 - Starting a new game
 - Make a guess
 - Retrieve state of in progress games
 - Listing in-progress games

## Database:
The var folder holds two databases which contains the following tables:
1) users.db
- users
2) games.db 
- users
- games
- game_states
- game_history
- valid_words

## Functionality
 User Registration:
 * User will have unique username and password
 * password is hashed with pbkdf2 and stored
 * if username is unique, return success or else failure

 User HTTP Basic Authentication:
 * User has to fill in the username and password as registered.
   This is authenticated via an external service, i.e., HTTP basic authentication dialog box when the service is opened in browser.

 Sign in:
 * Api will check username, password and request.auth object
 * Returns 200, if authenticated also returns `{ "authenticated" : true }` or else 401 `{ "error": "Unauthorized: Incorrect password." }`

 Create Game:
 * Used to start a new game with a random guess by user
 * If username is correct returns:
 
    ```http://tuffix-vm:5000
    {
        "completed": false,
        "correct": "?????",
        "gameid": ,
        "guesses": 6,
        "incorrect": "?????"
    }
    ```

List in progress games:
* Displays in progress games for a particular user(whose number of guess remaining is not 0)
* If user has pending games, return 200 
    
    ```
    {
        "gameid": gameid,
        "username": "username"
    }
    ```

* If user has no games pending, return 404 

    ```
    {
        "error": "Not Found: No games in progress for that user."
    }
    ```

Retrieve game state:
* Show the current state of game for a given gameid
* If game is finished then guesses field is 0 or else 0> guesses <=6
* Returns 200, 

    ``` 
    { 
        "completed": false,
        "correct": "?????",
        "gameid": gameid,
        "guesses": 6,
        "incorrect": "?????"
    }
    ```

Make a guess:
* If guess made by user is correct then return 200 OK with 

    ```
    {
        "completed": true,
        "correct": "secretword",
        "gameid": 3,
        "guesses": 5,
        "incorrect": "?????"
    }
    ```

* If user guess involves less/more letters (>5 or <5) then return

    ```
    {
        "error": "Bad Request: Guess must be 5 letters long."
    }
    ```

* If guess is not a valid word then return 400, 
    ```
    {
        "error": "Bad Request: Guess is not a valid word."
    }
    ```








 

