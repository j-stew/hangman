from random import randint
from datetime import datetime

from flask.ext.sqlalchemy import SQLAlchemy
from hangman import hangman_app
from flask import session

db = SQLAlchemy(hangman_app)
db.create_all()

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
		return "username={}, password={}, wins={}, loses={}".format(self.username,
			self.password, self.wins, self.loses)

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
		self.answer=Word.random_word(user)
		self.user_id=user.id

	def __repr__(self):
		return "created_date={}, status={}, answer={}.".format(self.created_date, self.status, self.answer)

class Guesses(db.Model):
	"""1-to-1 relationship with Game, isolated due to guess-specific computation.
	Object name is plural to differentiate from singular guesses made by user. Guesses
	contains the current game progress given user guesses.
	"""
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
		return "answer={}. correct_guesses={}, incorrect_guesses={}. remaining_guesses={}.".format(self.answer,
			self.correct_guesses, self.incorrect_guesses, self.remaining_guesses)

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

	def reset(self, answer):
		self.answer=answer
		self.correct_guesses=self.get_blanks()
		self.incorrect_guesses=''
		self.remaining_guesses=self.possible_guesses()

class Word(db.Model):
	"""Word bank of possible words for game, pulled from words.txt"""
	id = db.Column(db.Integer, primary_key=True)
	word = db.Column(db.String(200), nullable=False)

	def __init__(self, word):
		self.word=word

	def __repr__(self):
		return "word={}".format(self.word)

	@classmethod
	def random_word(cls, user):
		past_words=[game.answer for game in user.games.all()]
		word=None
		while word==None or word in past_words:
			num = randint(1, cls.query.count()+1)
			word=cls.query.filter_by(id=num).first().word
		return word

	@staticmethod
	def add_words():
		words = open("hangman/words.txt", "r").read().split("\n")
		for word in words:
			db.session.add(Word(word))
		db.session.commit()

db.create_all()
Word.add_words()
