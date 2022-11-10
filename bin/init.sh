#!/bin/sh

echo "Initializing database..."
sqlite3 ./var/wordle.db < ./share/wordle.sql
echo "Successfully initialized database."
echo "Populating database with words..."
python3 ./share/populate.py