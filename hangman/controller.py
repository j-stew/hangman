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
		if not session.get('user_id'):
			flash('Must login to play')
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return wrapper

############
###ROUTES###
############
@hangman_app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'GET':
		return render_template('login.html')

	username, password = request.form.get('username'), request.form.get('password')

	if not model.User.get_user(username):
		flash("Username not found. Please create account.")
		return redirect(url_for('signup'))

	if model.User.get_user(username).password != password:
	 	flash("Password invalid. Please try again.")
	 	return redirect(url_for('login'))

	session['user_id'] = model.User.query.filter_by(username=username).first().id
	return redirect(url_for('play'))

@hangman_app.route("/signup", methods=["GET", "POST"])
def signup():
	if request.method == 'GET':
		return render_template('signup.html')

	username, password = request.form.get('username'), request.form.get('password')

	if model.User.get_user(username):
		flash("Username already exists. Please try again.")
		return redirect(url_for('signup'))
	else:
		new_user = model.User(username, password)
		model.db.session.add(new_user)
		model.db.session.commit()
		session['user_id'] = model.User.query.filter_by(username=username).first().id
		return redirect(url_for('play'))

@hangman_app.route("/logout", methods=["GET", "POST"])
def logout():
	session.clear()
	return redirect(url_for("login"))

@hangman_app.route("/play", methods=["GET", "POST"])
@auth
def play():
	if not session.get('game_id'):
		game = model.Game(status='in-progress', user=model.User.query.filter_by(id=session['user_id']).first())
		model.db.session.add(game)
		model.db.session.commit()
		guesses = model.Guesses(game)
		model.db.session.add(guesses)
		model.db.session.commit()
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

	if request.form.get('guess'):
		if len(request.form.get('guess')) > 1:
			flash('Please guess a single letter.')
			return redirect(url_for('play'))
		elif request.form.get('guess') not in 'abcdefghijklmnopqrstuvwxyz':
			flash('Please guess a letter, not punction or numbers.')
			return redirect(url_for('play'))

	guess = request.form.get('guess')
	guesses = model.Guesses.query.filter_by(id=session['guesses_id']).first()
	user = model.User.query.filter_by(id=session['user_id']).first()
	if guess in guesses.incorrect_guesses:
		flash('"{}" already guessed. Please guess a new letter.'.format(guess))
		return redirect(url_for('play'))

	guesses.process_guess(guess)
	model.db.session.commit()
	game = model.Game.query.filter_by(id=session['game_id']).first()

	if "___" not in guesses.correct_guesses:
		game.status='win'
		user.wins += 1
		model.db.session.commit()
		del session['game_id']
		return redirect(url_for('win'))
	elif guesses.remaining_guesses <= 0:
		game.status='loss'
		user.loses += 1
		model.db.session.commit()
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
