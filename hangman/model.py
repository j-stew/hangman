from random import randint
from datetime import datetime

from flask.ext.sqlalchemy import SQLAlchemy
from hangman import hangman_app

db = SQLAlchemy(hangman_app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(140), nullable=False)
	wins = db.Column(db.Integer, default=0)
	loses = db.Column(db.Integer, default=0)
	games = db.relationship('Game', backref='user', lazy='dynamic')

	def __init__(self, username, password):
		self.username=username
		self.password=password
		self.wins=0
		self.loses=0

	def __repr__(self):
		return "User {}".format(self.username)

	# buggy
	def active_game(self):
		games = Game.query.filter_by(username=self.username)
		most_recent = games.filter_by(status='in-progress').order_by(Game.created_date.desc()).first()
		return most_recent

	def latest_game(self):
		return Game.query.filter_by(username=self.username).order_by(Game.created_date.desc()).first()

class Game(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	created_date = db.Column(db.DateTime, default=datetime.utcnow())
	status = db.Column(db.String(40), nullable=False)
	answer = db.Column(db.String(200), nullable=False)
	guesses = db.relationship('Guesses', backref='game', uselist=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __init__(self, status, user):
		self.created_date=datetime.utcnow()
		self.status=status
		self.answer=Word.random_word()
		self.user_id=user.id

	def __repr__(self):
		return "{} has status {}.".format(self.user.username, self.status)

class Guesses(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	answer = db.Column(db.String(200), nullable=False)
	correct_guesses = db.Column(db.String(200))
	incorrect_guesses = db.Column(db.String(400))
	remaining_guesses = db.Column(db.Integer, nullable=False)
	game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

	def __init__(self, game):
		self.answer=game.answer
		self.correct_guesses=self.get_blanks()
		self.incorrect_guesses=''
		self.remaining_guesses=self.possible_guesses()
		self.game_id=game.id

	def __repr__(self):
		return "Progress is {}".format(self.correct_guesses)

	def possible_guesses(self):
		return len(self.answer)

	def get_blanks(self):
		return " ".join(["___" for char in self.answer])

	def insert_correct_guess(self, guess):
		inserted = self.correct_guesses.split(" ")
		positions = [i for i, char in enumerate(self.answer) if char == guess]
		for position in positions:
			inserted[position] = guess
		self.correct_guesses = " ".join(inserted)

class Word(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	word = db.Column(db.String(200), nullable=False)

	def __init__(self, word):
		self.word=word

	def __repr__(self):
		return self.word

	@classmethod
	def random_word(cls):
		num = randint(1, cls.query.count()+1)
		return cls.query.filter_by(id=num).first().word

# db.drop_all()
db.create_all()
words = open("hangman/words.txt", "r").read().split("\n")
for word in words:
	db.session.add(Word(word))
db.session.commit()
