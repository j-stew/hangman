#!bin/sh
pip install -r requirements.txt

export DATABASE_URL=postgres://localhost/hangman
export DEBUG=True
export HOST=127.0.0.1
export PORT=5000

psql -c 'CREATE DATABASE hangman'
psql -c 'CREATE DATABASE test_hangman'
