from functools import wraps
from random import randint
from flask import render_template, redirect, request, flash, session, url_for

from hangman import hangman_app
from model import User
from controller import validate_signup, validate_login, validate_guess, get_user, \
get_guesses, get_game, create_game, create_user, check_guess, update_game

######################
###HELPER FUNCTIONS###
######################
def auth(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if not session.get('user_id'):
			flash('Must login to play')
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return wrapper

############
###ROUTES###
############
@hangman_app.route("/signup", methods=["GET", "POST"])
def signup():
	if request.method == 'GET':
		return render_template('signup.html')

	username, password = request.form.get('username'), request.form.get('password')
	if validate_signup(username, password):
		message, url = validate_signup(username, password)
		flash(message)
		return redirect(url_for(url))
	create_user(username, password)
	session['user_id'] = get_user(username).id
	return redirect(url_for('play'))

@hangman_app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'GET':
		return render_template('login.html')

	username, password = request.form.get('username'), request.form.get('password')
	if validate_login(username, password):
		message, url = validate_login(username, password)
		flash(message)
		return redirect(url_for(url))
	session['user_id'] = get_user(username).id
	return redirect(url_for('play'))

@hangman_app.route("/logout", methods=["GET", "POST"])
def logout():
	session.clear()
	return redirect(url_for("login"))

@hangman_app.route("/play", methods=["GET", "POST"])
@auth
def play():
	if not session.get('game_id'):
		game, guesses=create_game(session['user_id'])
		session['game_id']=game.id
		session['guesses_id']=guesses.id
		return render_template('play.html', answer=guesses.answer,
			remaining_guesses=guesses.remaining_guesses,
			correct_guesses=guesses.correct_guesses,
			incorrect_guesses=guesses.incorrect_guesses
			)

	if request.method=='GET':
		game = get_game(session['game_id'])
		guesses = get_guesses(session['guesses_id'])
		return render_template('play.html', answer=guesses.answer,
			remaining_guesses=guesses.remaining_guesses,
			correct_guesses=guesses.correct_guesses,
			incorrect_guesses=guesses.incorrect_guesses
			)

	guess = request.form.get('guess')
	guesses = get_guesses(session['guesses_id'])
	user = get_user(session['user_id'])
	game = get_game(session['game_id'])

	if guess:
		if validate_guess(guess, guesses):
			flash(validate_guess(guess, guesses))
			return redirect(url_for('play'))
		check_guess(guess, guesses)

	if update_game(game, guesses, user):
		del session['game_id']
		return redirect(url_for(update_game(game, guesses, user)))
	else:
		return redirect(url_for('play'))

@hangman_app.route("/win")
@auth
def win():
	if session.get('game_id'):
		return redirect(url_for('play'))
	guesses = get_guesses(session['guesses_id'])
	return render_template("win.html", answer=guesses.answer)

@hangman_app.route("/loss")
@auth
def loss():
	if session.get('game_id'):
		return redirect(url_for('play'))
	guesses = get_guesses(session['guesses_id'])
	return render_template("loss.html", answer=guesses.answer, correct_guesses=guesses.correct_guesses)

@hangman_app.route("/scores")
@auth
def scores():
	scores = User.query.order_by(User.wins.desc()).all()
	top_scores = scores[0:5]
	return render_template("scores.html", top_scores=top_scores)
