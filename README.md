# 449-Project-2

# Team members:
1. Ashley Thorlin
2. 

## Documentation
Procfile and .env from https://github.com/ProfAvery/cpsc449/tree/master/quart/hello

# Introduction
The goal is to Design endpoints for an application similar to Wordle.It will allow user to play more than one game in a day unlike the orignal wordle. The user will get overall six chances to guess the correct word. The guesses will be matched against the secret word to determine if it is correct or incorrect. If it's correct, the game will stop and if it is incorrect the user will get their remaining chances to guess.
The implementation of API is done in Python using the Quart framework and some ancillary tools like Foreman and sqlite3. The project also requires to create relational database schemas for the API implementation.

# How to initialize
To initialize the sqlite database, navigate to the project directory using a terminal and then type in `./bin/init.sh` or `sh ./bin/init.sh` and then create a locally hosted server by using `foreman start`

# How to use endpoints
  HTTP verbs | endpoints | Action 

- To register a new user: `http POST localhost:5000/auth/register username={user} password={pass}`
- To sign in: `http -a {username}:{password} localhost:5000/auth/signin`
- To create a game: `http POST localhost:5000/games/create username={username}`
- To make a guess: `http POST localhost:5000/games/{gameid} guess={guess}`  
- To list in-progress games : `http GET localhost:5000/users/{username}`
- To retrieve game state : `http GET localhost:5000/games/{gameid}`

Furthermore, you can view these endpoints in Quart Schema Documentation form when the server is running by navigating to `localhost:5000/docs` in a web browser!

 # Features:
 Creating a RESTful API that perform the following functionalities:

 - User registration
 - User Signin(Authentication with password hashing)
 - Starting a new game
 - Make a guess
 - Retrieve state of in progress games
 - Listing in-progress games

# Database:
The var folder holds wordle.db which contains the following tables:
- users
- games
- game_states
- valid_words

# Functionality
 User Registration:
 * User will have unique username and password
 * password is hashed with pbkdf2 and stored
 * if username is unique, return success or else failure

 Sign in:
 * Api will check username, password and request.auth object
 * Returns 200, if authenticated also returns `{ "authenticated" : true }` or else 401 `{ "error": "Unauthorized: Incorrect password." }`

 Create Game:
 * Used to start a new game with a random guess by user
 * If username is correct returns:
 
    ```
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








 

