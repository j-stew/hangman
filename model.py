from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from hangman import hangman_app

db = SQLAlchemy(hangman_app)

'''
Setup:
db.create_all()

words = open("hangman/words.txt", "r").read().split("', '")

for word in words:
	db.session.add(Word(word))
db.session.commit()
'''

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(140))
	wins = db.Column(db.Integer)
	loses = db.Column(db.Integer)

	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.wins = 0
		self.loses = 0

	def __repr__(self):
		return "User {}".format(self.username)

class Game(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	status = db.Column(db.String(4))
	guessed = db.Column(db.String(200))
	answer = db.Column(db.String(200))
	username = db.Column(db.String(80))

	def __init__(self, status, guessed, answer, username):
		self.status = status
		self.guessed = guessed
		self.answer = answer
		self.username = username

	def __repr__(self):
		return "{} guessed {} which was a {}.".format(self.username, self.guessed, self.status)

class Word(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	word = db.Column(db.String(200))

	def __init__(self, word):
		self.word = word

	def __repr__(self):
		return self.word

	@property
	def possible_guesses(self):
		return len(self.word)

	@property
	def blanks(self):
		return " ".join(["___" for char in self.word])
