PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS valid_words;
DROP TABLE IF EXISTS game_history;
DROP TABLE IF EXISTS game_states;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    PRIMARY KEY(username)
);

CREATE TABLE games (
    game_id INTEGER NOT NULL,
    secret_word TEXT NOT NULL,
    username TEXT NOT NULL,
    PRIMARY KEY(game_id),
    FOREIGN KEY(username) REFERENCES users(username)
);

CREATE TABLE game_states (
    game_id INTEGER NOT NULL,
    remaining_guesses TINYINT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

CREATE TABLE game_history (
    game_id INTEGER NOT NULL,
    guess TEXT NOT NULL,
    remaining_guesses TINYINT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

CREATE TABLE valid_words (
    word TEXT NOT NULL,
    correct_word BOOLEAN NOT NULL,
    PRIMARY KEY(word)
);

-- username: john, password: doe
INSERT INTO users VALUES ("john", "ecba7dc9b7edd8b83280c73677b2f63f$066614f195cf25cdea24d79771249f923044c9067bd9e0e84a3aa5824b39fb07");
INSERT INTO games VALUES (1, "cigar", "john");
INSERT INTO game_states VALUES (1, 2, "In Progress");
INSERT INTO game_history VALUES (1, "cited", 5);
INSERT INTO game_history VALUES (1, "amice", 4);
INSERT INTO game_history VALUES (1, "baccy", 3);
INSERT INTO game_history VALUES (1, "aglet", 2);
INSERT INTO games VALUES (2, "rebut", "john");
INSERT INTO game_states VALUES (2, 0, "lost");
INSERT INTO game_history VALUES (2, "aahed", 5);
INSERT INTO game_history VALUES (2, "aalii", 4);
INSERT INTO game_history VALUES (2, "aapas", 3);
INSERT INTO game_history VALUES (2, "aargh", 2);
INSERT INTO game_history VALUES (2, "aarti", 1);
INSERT INTO game_history VALUES (2, "abaca", 0);
INSERT INTO games VALUES (3, "sissy", "john");
INSERT INTO game_states VALUES (3, 5, "won");
INSERT INTO game_history VALUES (3, "sissy", 5);
INSERT INTO games VALUES (4, "humph", "john");
INSERT INTO game_states VALUES (4, 5, "In Progress");
INSERT INTO game_history VALUES (4, "bahus", 5);


COMMIT;