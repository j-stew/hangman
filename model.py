from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from hangman import hangman_app

db = SQLAlchemy(hangman_app)
# db.create_all()

# words = open("words.txt", "r").read().split("', '")

# for word in words:
# 	model.db.session.add(model.Word(word))
# model.db.session.commit()

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

	@property
	def blanks(self):
		return " ".join(["___" for char in self.word])

	def char_replace(self, guessed, guess):
		guessed = guessed.split(" ") # ["___","___","___","___"]
		char_positions = [i for i, char in enumerate(self.word) if char == guess] # [0, 3]
		return 'debug' ## " ".join([guessed[position] = guess for position in char_position])

	def add_game(game_type, game, guessed, answer, username):
		game = model.Game(game_type, guessed, answer, username)
		model.db.session.add(game)
		user = model.User.query.filter_by(username=session.username).first()
		## user.loses += 1 if game_type == 'loss' else user.wins += 1
		if game_type == 'loss':
			user.loses += 1
		else:
			user.wins += 1
		model.db.session.commit()

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