PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS users;

CREATE TABLE users (
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    PRIMARY KEY(username)
);

-- username: john, password: doe
INSERT INTO users VALUES ("john", "ecba7dc9b7edd8b83280c73677b2f63f$066614f195cf25cdea24d79771249f923044c9067bd9e0e84a3aa5824b39fb07");

COMMIT;