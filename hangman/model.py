from random import randint
from datetime import datetime
from os import stat

from flask.ext.sqlalchemy import SQLAlchemy
from hangman import hangman_app
from flask import session

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
		return "username={}, password={}, wins={}, loses={}".format(self.username,
			self.password, self.wins, self.loses)

class Word(db.Model):
	"""Word bank of possible words for game, pulled from words.txt"""
	id = db.Column(db.Integer, primary_key=True)
	added_date = db.Column(db.DateTime)
	word = db.Column(db.String(200), nullable=False, unique=True, index=True)

	def __init__(self, added_date, word):
		self.added_date=added_date
		self.word=word

	def __repr__(self):
		return "added_date={}, word={}".format(self.added_date, self.word)

	@classmethod
	def add_words(cls):
		added_date=datetime.utcfromtimestamp(stat('hangman/words.txt').st_mtime)
		if not cls.query.first():
			words = set(open("hangman/words.txt", "r").read().split("\n"))
			added_date=datetime.utcfromtimestamp(stat('hangman/words.txt').st_mtime)
			for word in words:
				db.session.add(Word(added_date, word))
			db.session.commit()
		elif added_date > cls.query.order_by(cls.added_date.desc()).first().added_date:
			file_words = set(open("hangman/words.txt", "r").read().split("\n"))
			db_words = [word.word for word in cls.query.all()]
			new_words = file_words.difference(db_words)
			if new_words:
				for word in new_words:
					if not cls.query.filter_by(word=word).first():
						db.session.add(Word(added_date,word))
				db.session.commit()

	@classmethod
	def random_word(cls):
		num = randint(1, cls.query.count()+1)
		return cls.query.filter_by(id=num).first()

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
		self.answer=self.select_word(user)
		self.user_id=user.id

	def __repr__(self):
		return "created_date={}, status={}, answer={}.".format(self.created_date, self.status, self.answer)

	def select_word(self, user):
		past_words=[game.answer for game in Game.query.filter_by(user=user).all()]
		word=None
		total_words=Word.query.count()
		i=0
		while word==None:
			try:
				word=Word.random_word().word
			except AttributeError:
				word=Word.random_word().word
			if word in past_words:
				word=None
				i+=1
			if i >= total_words:
				return "You've used all the words in the word bank!"
		return word

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

# db.session.remove()
# db.drop_all()
db.create_all()
Word.add_words()