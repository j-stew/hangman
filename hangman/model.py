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
	games = db.relationship("Game", backref="user", lazy="dynamic")

	def __init__(self, username, password, wins=0, loses=0):
		self.username=username
		self.password=password
		self.wins=wins
		self.loses=loses

	def __repr__(self):
		return "User {}".format(self.username)

class Game(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	created_date = db.Column(db.DateTime, default=datetime.utcnow())
	status = db.Column(db.String(40))
	guessed = db.Column(db.String(200))
	answer = db.Column(db.String(200))
	remaining_guesses = db.Column(db.Integer)
	incorrectly_guessed = db.Column(db.String(400))
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

	def __init__(self, status, guessed, answer, remaining_guesses, incorrectly_guessed):
		self.status=status
		self.guessed=guessed
		self.answer=answer
		self.remaining_guesses=remaining_guesses
		self.incorrectly_guessed=incorrectly_guessed

	def __repr__(self):
		return "Guessed {} which was status {}.".format(self.guessed, self.status)

class Word(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	word = db.Column(db.String(200), nullable=False)

	def __init__(self, word):
		self.word=word

	def __repr__(self):
		return self.word

	@property
	def possible_guesses(self):
		return len(self.word)

	@property
	def blanks(self):
		return " ".join(["___" for char in self.word])

	@classmethod
	def random_word(cls):
		num = randint(1, cls.query.count()+1)
		return cls.query.filter_by(id=num).first()

db.create_all()
words = open("hangman/words.txt", "r").read().split("\n")
for word in words:
	db.session.add(Word(word))
db.session.commit()
