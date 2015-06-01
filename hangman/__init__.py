import os
from flask import Flask

hangman_app = Flask(__name__)

hangman_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
hangman_app.config['SECRET_KEY'] = '678297'
hangman_app.config['DEBUG'] = True

from hangman import model, controller
