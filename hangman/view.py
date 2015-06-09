from functools import wraps
from random import randint
from flask import render_template, redirect, request, flash, session, url_for

from hangman import hangman_app
import model
import controller

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
	controller.validate_signup(username, password)
	controller.create_user(username, password)
	session['user_id'] = controller.get_user(username).id
	return redirect(url_for('play'))

@hangman_app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'GET':
		return render_template('login.html')

	username, password = request.form.get('username'), request.form.get('password')
	controller.validate_login(username, password)
	session['user_id'] = controller.get_user(username).id
	return redirect(url_for('play'))

@hangman_app.route("/logout", methods=["GET", "POST"])
def logout():
	session.clear()
	return redirect(url_for("login"))

@hangman_app.route("/play", methods=["GET", "POST"])
@auth
def play():
	if not session.get('game_id'):
		game, guesses=controller.create_game(session['user_id'])
		session['game_id']=game.id
		session['guesses_id']=guesses.id
		return render_template('play.html', answer=guesses.answer,
			remaining_guesses=guesses.remaining_guesses,
			correct_guesses=guesses.correct_guesses,
			incorrect_guesses=guesses.incorrect_guesses
			)

	if request.method=='GET':
		game = model.Game.query.filter_by(id=session['game_id']).first()
		guesses = model.Guesses.query.filter_by(id=session['guesses_id']).first()
		return render_template('play.html', answer=guesses.answer,
			remaining_guesses=guesses.remaining_guesses,
			correct_guesses=guesses.correct_guesses,
			incorrect_guesses=guesses.incorrect_guesses
			)

	guess = request.form.get('guess')
	guesses = controller.get_guesses(session['guesses_id'])
	user = controller.get_user(session['user_id'])
	game = controller.get_game(session['game_id'])

	if guess:
		controller.validate_guess(guess)
		controller.check_guess(guess, guesses)

	if controller.update_game(game, guesses, user)=='win':
		del session['game_id']
		return redirect(url_for('win'))
	elif controller.update_game(game, guesses)=='loss':
		del session['game_id']
		return redirect(url_for('loss'))
	else:
		return redirect(url_for('play'))

@hangman_app.route("/win")
@auth
def win():
	if session.get('game_id'):
		return redirect(url_for('play'))
	guesses = model.Guesses.query.filter_by(id=session['guesses_id']).first()
	return render_template("win.html", answer=guesses.answer)

@hangman_app.route("/loss")
@auth
def loss():
	if session.get('game_id'):
		return redirect(url_for('play'))
	guesses = model.Guesses.query.filter_by(id=session['guesses_id']).first()
	return render_template("loss.html", answer=guesses.answer, correct_guesses=guesses.correct_guesses)

@hangman_app.route("/scores")
@auth
def scores():
	scores = model.User.query.order_by(model.User.wins.desc()).all()
	top_scores = scores[0:5]
	return render_template("scores.html", top_scores=top_scores)
