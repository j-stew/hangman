from flask import Flask

hangman_app = Flask(__name__)

hangman_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jessicastewart:r0llr0ll123@localhost:5432/hangman'
hangman_app.config['SECRET_KEY'] = '678297'
hangman_app.config['DEBUG'] = True

from hangman import model, controller
