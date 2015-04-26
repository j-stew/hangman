from flask import Flask

hangman_app = Flask(__name__)

hangman_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////hangman.db'
hangman_app.config['SQLALCHEMY_ECHO'] = True
hangman_app.config['DEBUG'] = True

# from hangman import model, controller