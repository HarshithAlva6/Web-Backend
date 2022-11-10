PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS game_instances;
DROP TABLE IF EXISTS game_states;
DROP TABLE IF EXISTS game_history;
DROP TABLE IF EXISTS valid_words;

CREATE TABLE game_instances(
    game_id INTEGER NOT NULL,
    secret_word TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    PRIMARY KEY(game_id),
);

CREATE TABLE game_states (
    game_id INTEGER NOT NULL,
    remaining_guesses TINYINT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES game_instances(game_id)
);

CREATE TABLE game_history (
    game_id INTEGER NOT NULL,
    guess TEXT NOT NULL,
    remaining_guesses TINYINT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES game_instances(game_id)
);

CREATE TABLE valid_words (
    word TEXT NOT NULL,
    correct_word BOOLEAN NOT NULL,
    PRIMARY KEY(word)
);

INSERT INTO game_instances VALUES (1, "cigar", "john", "doe");
INSERT INTO game_states VALUES (1, 2, "In Progress");
INSERT INTO game_history VALUES (1, "cited", 5);
INSERT INTO game_history VALUES (1, "amice", 4);
INSERT INTO game_history VALUES (1, "baccy", 3);
INSERT INTO game_history VALUES (1, "aglet", 2);
INSERT INTO game_instances VALUES (2, "rebut", "john", "doe");
INSERT INTO game_states VALUES (2, 0, "lost");
INSERT INTO game_history VALUES (2, "aahed", 5);
INSERT INTO game_history VALUES (2, "aalii", 4);
INSERT INTO game_history VALUES (2, "aapas", 3);
INSERT INTO game_history VALUES (2, "aargh", 2);
INSERT INTO game_history VALUES (2, "aarti", 1);
INSERT INTO game_history VALUES (2, "abaca", 0);
INSERT INTO game_instances VALUES (3, "sissy", "john", "doe");
INSERT INTO game_states VALUES (3, 5, "won");
INSERT INTO game_history VALUES (3, "sissy", 5);
INSERT INTO game_instances VALUES (4, "humph", "john", "doe");
INSERT INTO game_states VALUES (4, 5, "In Progress");
INSERT INTO game_history VALUES (4, "bahus", 5);


COMMIT;