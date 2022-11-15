import databases
import dataclasses
import sqlite3
import json
import toml
import hashlib
import secrets

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
class User:
    username: str
    password: str


# ---------------------------------------------------------------------------- #
#                                 helper funcs                                 #
# ---------------------------------------------------------------------------- #

# functions to hash and verify from https://til.simonwillison.net/python/password-hashing-with-pbkdf2
async def _hash_password(password: str, salt: str = None):
    if not salt:
        salt = secrets.token_hex(16)

    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()

    return f"{salt}${pw_hash}"


async def _get_games_db():
    db = g._database = databases.Database(app.config["DATABASES"]["GAMES_URL"])
    await db.connect()
    return db

async def _get_users_db():
    db = g._database = databases.Database(app.config["DATABASES"]["USERS_URL"])
    await db.connect()
    return db


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

# --------------------------------- register --------------------------------- #
@app.route("/auth/register", methods=["POST"])
@tag(["auth"])
@validate_request(User)
@validate_response(User, 201)
@validate_response(Error, 400)
@validate_response(Error, 409)
async def register_user(data):
    """Register a new user with a username and password."""
    userdb = await _get_users_db()
    gamedb = await _get_games_db()
    user = dataclasses.asdict(data)

    # verify user input
    if not user["username"] or not user["password"]:
        abort(400, "Username and password cannot be empty.")

    # hash password
    hashed_pw = await _hash_password(user["password"])
    user["password"] = hashed_pw
    user["username"] = user["username"].lower()

    # insert username/password into users in users.db
    try:
        id = await userdb.execute(
            """
            INSERT INTO users(username, password)
            VALUES(:username, :password)
            """,
            user,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    try:
        id = await gamedb.execute(
            """
            INSERT INTO users(username, password)
            VALUES(:username, :password)
            """,
            user,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)
        
    # TODO: possibly change location to /games/<username>
    return user, 201, {"Location": f"/users/{user['username']}"}

# ---------------------------------- sign in --------------------------------- #
@app.route("/auth/signin")
@tag(["auth"])
@validate_response(AuthorizedUser, 200)
@validate_response(Error, 400)
@validate_response(Error, 401)
async def signin():
    """
    Check if a username/password combination is valid.
    Uses Basic Auth passed through Authorization header.
    """

    auth = request.authorization

    # return bad request if invalid auth header
    if not auth:
        abort(400, "Authorization header is required.")

    # check both username and password are present
    if not auth.username or not auth.password:
        abort(400, "Username and password are required.")

    db = await _get_users_db()

    # fetch the row for the entered username
    user_row = await db.fetch_one(
        """
        SELECT *
        FROM users
        WHERE username = :username
        """,
        {"username": auth.username},
    )

    app.logger.info(
        """
        SELECT *
        FROM users
        WHERE username = :username
        """,
        {"username": auth.username},
    )

    # if the username doesn't exist, return unauthorized
    if not user_row:
        abort(401, "Username does not exist.")

    # compute the hash of the entered password
    stored_pw = user_row[1]
    salt = stored_pw.split("$")[0]
    computed_hash = await _hash_password(auth.password, salt)

    # if the computed hash doesn't match the stored hash, return unauthorized
    if not secrets.compare_digest(computed_hash, stored_pw):
        abort(401, "Incorrect password.")

    # finally, return authenticated = true
    return {"authenticated": True}, 200

