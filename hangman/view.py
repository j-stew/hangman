"""
User, game and guess IDs stored in HTTP session cookie. Game-state persists on page
re-load but not on logout.
"""

from functools import wraps
from random import randint
from flask import render_template, redirect, request, flash, session, url_for

from hangman import hangman_app
from model import User
from controller import validate_signup, validate_login, validate_guess, get_user, \
get_guesses, get_game, create_game, create_user, update_guesses, check_game, update_game

def auth(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if not get_user(session.get('user_id')):
			flash('Must login to play')
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return wrapper

@hangman_app.route("/")
def index():
	return redirect(url_for('login'))

@hangman_app.route("/signup", methods=["GET", "POST"])
def signup():
	if request.method == 'GET':
		return render_template('signup.html')

	username, password, confirm_password = request.form.get('username'), request.form.get('password'), request.form.get('confirm_password')
	if validate_signup(username, password, confirm_password):
		message= validate_signup(username, password, confirm_password)
		flash(message)
		return redirect(url_for('signup'))
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
	if not get_game(session.get('game_id')):
		game, guesses=create_game(session['user_id'])
		session['game_id']=game.id
		session['guesses_id']=guesses.id
		return render_template('play.html', guesses=guesses)

	if request.method=='GET':
		game = get_game(session['game_id'])
		guesses = get_guesses(session['guesses_id'])

		if request.args.get('answer'):
			game.change_answer(request.args.get('answer'))
		return render_template('play.html', guesses=guesses)

	guess = request.form.get('guess').lower()
	guesses = get_guesses(session['guesses_id'])
	user = get_user(session['user_id'])
	game = get_game(session['game_id'])

	if guess:
		if validate_guess(guess, guesses):
			flash(validate_guess(guess, guesses))
			return redirect(url_for('play'))
		else:
			update_guesses(guess, guesses)

	if check_game(guesses):
		del session['game_id']
		return redirect(url_for(update_game(guesses)))
	else:
		return redirect(url_for('play'))

@hangman_app.route("/win")
@auth
def win():
	if get_game(session.get('game_id')):
		return redirect(url_for('play'))
	guesses = get_guesses(session['guesses_id'])
	return render_template("win.html", guesses=guesses)

@hangman_app.route("/loss")
@auth
def loss():
	if get_game(session.get('game_id')):
		return redirect(url_for('play'))
	guesses = get_guesses(session['guesses_id'])
	return render_template("loss.html", guesses=guesses)

@hangman_app.route("/scores")
@auth
def scores():
	scores = User.query.order_by(User.wins.desc()).all()
	top_scores = scores[0:5]
	return render_template("scores.html", top_scores=top_scores)
