import databases
import dataclasses
import sqlite3
import json
import toml
import uuid

from quart import Quart, g, request, abort, make_response
from quart_schema import (
    tag,
    validate_request,
    QuartSchema,
    validate_response,
)
from random import randint
from typing import Tuple
from logging.config import dictConfig

app = Quart(__name__)
QuartSchema(app)

app.config.from_file("./etc/wordle.toml", toml.load)

dictConfig({
    'version': 1,
    'loggers': {
        'quart.app': {
            'level': 'ERROR',
        },
    },
})


@dataclasses.dataclass
class Error:
    error: str


@dataclasses.dataclass
class AuthorizedUser:
    authenticated: bool


@dataclasses.dataclass
class Guess:
    guess: str


@dataclasses.dataclass
class User:
    username: str
    password: str


@dataclasses.dataclass
class CreateGame:
    username: str


@dataclasses.dataclass
class CreatedGame:
    game_id: str
    remaining_guesses: int = 6
    status: str = "In Progress"


@dataclasses.dataclass
class GameState:
    """The state of the game including information about last guess."""

    game_id: str
    guess: str
    correct_spots: str = "hel??"
    incorrect_spots: str = "?or??"
    remaining_guesses: int = 6


# ---------------------------------------------------------------------------- #
#                                 helper funcs                                 #
# ---------------------------------------------------------------------------- #

async def _get_games_db():

    db = g._database = databases.Database(app.config["DATABASES"]["GAMES_URL"])
    await db.connect()
    return db

async def _get_random_word():
    with open("./share/correct.json") as file:
        data = json.load(file)
        rand_index = randint(0, len(data) - 1)
        return data[rand_index]


async def _check_string(guess: str, goal: str) -> Tuple[str, str]:

    guess = guess.lower()

    if guess == goal:
        return (goal, "?????")

    # helper function to replace a character in an index of a string
    def replace_idx(s: str, idx: int, letter: str) -> str:
        return s[:idx] + letter + s[idx + 1 :]

    # create a hashmap of goal string and letter count
    goal_cnt = {}
    for letter in goal:
        goal_cnt[letter] = goal_cnt.get(letter, 0) + 1

    correct_spot = "?????"
    incorrect_spot = "?????"

    # first pass to check for correct spot which deals with duplicates,
    # ex: guess = "hello", goal = "world", we dont want to count the first 'l'.
    for i in range(len(guess)):
        if guess[i] == goal[i]:
            correct_spot = replace_idx(correct_spot, i, guess[i])
            goal_cnt[guess[i]] -= 1

    # second pass to check for incorrect spot
    for i in range(len(guess)):
        if guess[i] != goal[i] and goal_cnt.get(guess[i], 0) > 0:
            incorrect_spot = replace_idx(incorrect_spot, i, guess[i])
            goal_cnt[guess[i]] -= 1

    return (correct_spot, incorrect_spot)


# ---------------------------------------------------------------------------- #
#                                error handlers                                #
# ---------------------------------------------------------------------------- #
@app.errorhandler(400)
async def bad_request(e):
    return {"error": f"Bad Request: {e.description}"}, 400


@app.errorhandler(401)
async def unauthorized(e):
    response = await make_response({"error": f"Unauthorized: {e.description}"}, 401)
    response.status_code = 401
    response.headers["WWW-Authenticate"] = 'Basic realm="User Login"'
    return response


@app.errorhandler(404)
async def not_found(e):
    return {"error": f"Not Found: {e.description}"}, 404


@app.errorhandler(409)
async def username_exists(e):
    return {"error": "Username already exists"}, 409


# ---------------------------------------------------------------------------- #
#                                  api routes                                  #
# ---------------------------------------------------------------------------- #


@app.route("/games/testgame", methods=["GET"])
@tag(["games"])
async def test_game():
    app.logger.info("Games Test call")

    return "Games Test successful", 200

# -------------------------------- create game ------------------------------- #
@app.route("/games/create", methods=["POST"])
@tag(["games"])
@validate_request(CreateGame)
@validate_response(CreatedGame, 201)
@validate_response(Error, 400)
async def create_game(data):
    """Create a new game for a user with a random word."""
    game = dataclasses.asdict(data)
    game["secret_word"] = await _get_random_word()
    app.logger.warning(game)

    creategame = {
        "secret_word" : game["secret_word"],
        "username" : game["username"],
        "game_id" : str(uuid.uuid4())
    }
    db = await _get_games_db()

    username = await db.fetch_one(
        "SELECT * from users WHERE username = :username",
        values={"username": game["username"]},
    )

    app.logger.info(
        "SELECT * from users WHERE username = :username",
        {"username": game["username"]},
    )

    if username:
        # create new row in game
        await db.execute(
            """
            INSERT INTO games(secret_word, username, game_id)
            VALUES(:secret_word, :username, :game_id)
            """,
            creategame,
        )

        game_state = {
            "game_id": creategame["game_id"],
            "remaining_guesses": 6,
            "status": "In Progress",
        }
        app.logger.warning(game_state)
        # create new row in game_states
        await db.execute(
            """
            INSERT INTO game_states(game_id, remaining_guesses, status)
            VALUES(:game_id, :remaining_guesses, :status)
            """,
            game_state,
        )

        return game_state, 201, {"Location": f"/games/{creategame['game_id']}"}

    else:
        abort(404, "Username does not exist.")


# ---------------------------- retrieve game state --------------------------- #
@app.route("/games/<string:game_id>", methods=["GET"])
@tag(["games"])
@validate_response(Error, 404)
async def get_game_state(game_id):
    """Retrieve the history of a game or the result if it is over."""
    db = await _get_games_db()

    # we need all rows in game_history for the game_id
    # join with game_states and games to get secret_word, status, and remaining_guesses
    # [0] = game_id, [1] = guess, [2] = secret_word, [3] = status,
    # [4] = remaining_guesses in guess for history, [5] = remaining guesses in game_states
    game_states = await db.fetch_all(
        """
        SELECT
            game_states.game_id, game_history.guess, games.secret_word,
            game_states.status, game_history.remaining_guesses, 
            game_states.remaining_guesses
        FROM game_states
            INNER JOIN game_history ON game_states.game_id = game_history.game_id
            INNER JOIN games ON game_states.game_id = games.game_id
        WHERE game_states.game_id = :game_id
        """,
        values={"game_id": game_id},
    )

    app.logger.info(
        """
        SELECT
            game_states.game_id, game_history.guess, games.secret_word,
            game_states.status, game_history.remaining_guesses, 
            game_states.remaining_guesses
        FROM game_states
            INNER JOIN game_history ON game_states.game_id = game_history.game_id
            INNER JOIN games ON game_states.game_id = games.game_id
        WHERE game_states.game_id = :game_id
        """,
        {"game_id": game_id},
    )

    if game_states:
        response = []
        for state in game_states:
            if state[3] == "In Progress":
                evaluation = await _check_string(state[1], state[2])
                state_info = {
                    "game_id": state[0],
                    "guess": state[1],
                    "remaining_guesses": state[4],
                    "correct_spots": evaluation[0],
                    "incorrect_spots": evaluation[1],
                }
                response.append(state_info)
            elif state[3] == "won" or state[3] == "lost":
                return {
                    "game_id": state[0],
                    "status": state[3],
                    "remaining_guesses": state[5],
                }, 200
        return response, 200
    else:
        abort(404, "No game history found for given game id.")


# --------------------- make a guess / update game state --------------------- #
@app.route("/games/<string:game_id>", methods=["POST"])
@tag(["games"])
@validate_request(Guess)
@validate_response(Error, 400)
async def check_guess(data, game_id):
    """Make a guess for a game with a given game_id. Returns updated game state."""

    guess = await request.get_json()
    guess = guess["guess"]

    if len(guess) != 5:
        abort(400, "Guess must be 5 letters long.")

    db = await _get_games_db()

    # perform lookup in db table "game_states" to check if game is in progress
    status = await db.fetch_val(
        "SELECT game_states.status FROM game_states WHERE game_states.game_id = :game_id",
        values={"game_id": game_id},
    )

    app.logger.info(
        "SELECT game_states.status FROM game_states WHERE game_states.game_id = :game_id",
        {"game_id": game_id},
    )

    # if finished, then return number of guesses and game status
    if status != "In Progress":
        guesses = await db.fetch_val(
        "SELECT game_states.remaining_guesses FROM game_states WHERE game_states.game_id = :game_id",
        values={"game_id": game_id},
        )

        app.logger.info(
        "SELECT game_states.remaining_guesses FROM game_states WHERE game_states.game_id = :game_id",
        {"game_id": game_id},
        )

        return {"remaining_guesses" : guesses, "status": status}

    # perform lookup in db table "valid_words" to check if guess is valid
    valid_word = await db.fetch_val(
        "SELECT EXISTS(SELECT 1 FROM valid_words WHERE word = :word)",
        values={"word": guess},
    )

    app.logger.info(
        "SELECT EXISTS(SELECT 1 FROM valid_words WHERE word = :word)",
        {"word": guess},
    )

    # 0 if not in table, 1 if in table
    if valid_word == 0:
        abort(400, "Guess is not a valid word.")

    # fetch a tuple of (secret_word, remaining_guesses) from db
    info = await db.fetch_one(
        """
        SELECT secret_word, remaining_guesses
        FROM games INNER JOIN game_states ON games.game_id = game_states.game_id
        WHERE games.game_id = :game_id
        """,
        {"game_id": game_id},
    )

    app.logger.info(
        """
        SELECT secret_word, remaining_guesses
        FROM games INNER JOIN game_states ON games.game_id = game_states.game_id
        WHERE games.game_id = :game_id
        """,
        {"game_id": game_id},
    )

    if not info:
        abort(404, "Game with that id does not exist.")

    # check if there are any remaining_guesses left
    if info[1] > 0:
        # returns a tuple of formatted strings (correct_spots, incorrect_spots)
        # ex: ("?a???", "???b?") -> a is correct spot, b is incorrect spot
        state_fields = await _check_string(guess, info[0])

        # initialize game_state info
        game_info = {
            "game_id": game_id,
            "remaining_guesses": info[1] - 1,
            "status": "In Progress",
        }

        # insert into game_history
        await db.execute(
            """
            INSERT INTO game_history(game_id, guess, remaining_guesses)
            VALUES(:game_id, :guess, :remaining_guesses)
            """,
            values={
                "game_id": game_id,
                "guess": guess,
                "remaining_guesses": info[1] - 1,
            },
        )

        # check if the guess was correct
        if guess == info[0]:
            game_info["status"] = "won"
        else:
            if game_info["remaining_guesses"] == 0:
                game_info["status"] = "lost"

        # update the game_states table
        await db.execute(
            """
            UPDATE game_states
            SET status = :status, remaining_guesses = :remaining_guesses
            WHERE game_id = :game_id
            """,
            values=game_info,
        )

        # insert game_state info into response (correct_spots, incorrect_spots)
        game_info["correct_spots"] = state_fields[0]
        game_info["incorrect_spots"] = state_fields[1]
        game_info["guess"] = guess
    else:
        abort(400, "No guesses left.")

    return game_info, 200


# -----------------------------------Listing in progress games------------------------#
@app.route("/users/<string:username>", methods=["GET"])
async def get_progress_game(username):
    """Retrieve the list of games in progress for a user with a given username."""
    db = await _get_games_db()
    progress_game = await db.fetch_all(
        """
        SELECT games.game_id, username, remaining_guesses
        FROM games LEFT JOIN game_states ON games.game_id = game_states.game_id 
        WHERE username = :username AND game_states.status = 'In Progress'
        """,
        values={"username": username},
    )

    app.logger.info(
        """
        SELECT games.game_id, username, remaining_guesses
        FROM games LEFT JOIN game_states ON games.game_id = game_states.game_id 
        WHERE username = :username AND game_states.status = 'In Progress'
        """,
        {"username": username},
    )

    print("Progress of game1:", progress_game)
    if progress_game:
        print("Progress of game:", progress_game)
        return list(map(dict, progress_game))
    else:
        abort(404, "No games in progress for that user.")
