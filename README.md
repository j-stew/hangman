#!/bin/bash
git clone https://github.com/j-stew/hangman.git
cd hangman

virtualenv hangman_env
source hangman_env/bin/activate

pip install -r requirements.txt

export DATABASE_URL=postgres://localhost/hangman
export DEBUG=True
export HOST=127.0.0.1
export PORT=5000

psql -c 'CREATE DATABASE hangman'
psql -c 'CREATE DATABASE test_hangman'

python test_model.py
python test_controller.py
python test_view.py

python run.py
open http://127.0.0.1:5000/login
