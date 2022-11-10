#!/bin/sh

echo "Initializing users database..."
sqlite3 ./var/users.db < ./share/users.sql
echo "Initializing games database..."
sqlite3 ./var/games.db < ./share/games.sql
echo "Successfully initialized database."
echo "Populating database with words..."
python3 ./share/populate.py