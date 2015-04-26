from functools import wraps
from random import randint
from flask import render_template, redirect, request, flash, session, url_for

from hangman import hangman_app
import model

######################
###HELPER FUNCTIONS###
######################
def auth(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if session['username']:
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return wrapper

def validate_input(input):
	if request.form.get(input) == None:
		flash("Please input {}".format(input))
	else:
		return request.form.get(input)

def random_word():
	num = randint(1, model.Word.query.count()+1)
	return model.Word.query.filter_by(id=num).first()

############
###ROUTES###
############

@hangman-app.route("/login", methods=["GET", "POST"])
def login():
	username = validate_input('username')
	password = validate_input('password')

	db_username = model.User.query.filter_by(username=username).first()
	db_password = db_username.password

	if not db_username:
		flash("Username not found. Please create account.")

	if db_password != password:
		flash("Password not found. Please try again.")
	else:
		session['username'] = username
		return render_template("play.html", title="Play")

@hangman-app.route("/signup", methods=["GET", "POST"])
def signup():
	username = validate_input('username')
	password = validate_input('password')

	db_username = model.User.query.filter_by(username=username).first()

	if db_username:
		flash("Username already exists. Please try again.")
	else:
		new_user = model.User(username, password)
		model.db.session.add(new_user)
		model.db.session.commit()
		return render_template("play.html", title="Play")

@hangman-app.route("/logout", methods=["GET", "POST"])
def logout():
	session.pop('username')
	return redirect(url_for("login"))

@hangman-app.route("/play", methods=["GET", "POST"])
@auth
def play(guess=None, answer=None, guessed=None, incorrectly_guessed=None, remaining_guesses=None):
	if answer == None:
		answer = random_word()
		remaining_guesses = answer.possible_guesses
		guessed = answer.blanks()
		incorrectly_guessed = []
		answer = answer.word
	
	guess = validate_input('guess').lower()

	if len(guess) > 1:
		flash('Please guess a single letter.')

	if guess not in 'abcdefghijklmnopqrstuvwxyz':
		flash('Please guess a letter, not punction or numbers.')

	if guess in incorrectly_guessed:
		flash('{} already guessed. Please guess a new letter.'.format(guess))

	remaining_guesses -= 1

	if guess in answer:
		guessed = char_replace(guessed=guessed, guess=guess)
	else:
		incorrectly_guessed.append(guess)

	if "___" not in guessed:
		add_game('win', game, guessed, answer, session.username)
		return redirect(url_for('win'), answer)
	elif remaining_guesses == 0:
		add_game('loss', game, guessed, answer, session.username)
		return redirect(url_for('loss'), answer, guessed)
	else:
		return redirect(url_for('play'), guess=guess, answer=answer, guessed=guessed, incorrectly_guessed=incorrectly_guessed, remaining_guesses=remaining_guesses)

@hangman-app.route("/win")
@auth
def win(answer):
	return render_template("win.html", title="Win", answer=answer)

@hangman-app.route("/loss")
@auth
def loss(answer, guessed):
	return render_template("loss.html", title="Loss", answer=answer, guessed=guessed)

@hangman-app.route("/scores")
@auth
def scores():
	scores = model.User.query.order_by(model.User.wins.desc()).all()
	top_scores = scores[0:5]
	return render_template("scores.html", title="Scores", top_scores=top_scores)
