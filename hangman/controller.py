import model
from flask import flash, redirect, url_for

def create_game(user_id):
	game = model.Game(status='in-progress', user=model.User.query.filter_by(id=user_id).first())
	model.db.session.add(game)
	model.db.session.commit()
	guesses = model.Guesses(game)
	model.db.session.add(guesses)
	model.db.session.commit()
	return game, guesses

def create_password(username, password):
	new_user = model.User(username, password)
	model.db.session.add(new_user)
	model.db.session.commit()

def get_user(user):
	if model.User.query.filter_by(id=user_id).first():
		return model.User.query.filter_by(id=user_id).first()
	elif model.User.query.filter_by(username=user_id).first()
		return model.User.query.filter_by(username=user_id).first()

def get_game(game_id):
	return model.Game.query.filter_by(id=game_id).first()

def get_guesses(guesses_id):
	return model.Guesses.query.filter_by(id=guesses_id).first()

def validate_guess(guess, guesses):
	if len(guess) > 1:
		flash('Please guess a single letter.')
		return redirect(url_for('play'))
	elif guess not in 'abcdefghijklmnopqrstuvwxyz':
		flash('Please guess a letter, not punction or numbers.')
		return redirect(url_for('play'))
	elif guess in guesses.incorrect_guesses:
		flash('"{}" already guessed. Please guess a new letter.'.format(guess))
		return redirect(url_for('play'))

def check_guess(guess, guesses):
	guesses.remaining_guesses -= 1
	if guess in guesses.answer:
		guesses.insert_correct_guess(guess)
	else:
		guesses.incorrect_guesses += guess
	model.db.session.commit()

def update_game(game, guesses, user):
	if "___" not in guesses.correct_guesses:
		game.status='win'
		user.wins += 1
		model.db.session.commit()
		return 'win'
	elif guesses.remaining_guesses <= 0:
		game.status='loss'
		user.loses += 1
		model.db.session.commit()
		return 'loss'

def validate_login(given_username, given_password):
	if not controller.get_user(username=given_username):
		flash("Username not found. Please create account.")
		return redirect(url_for('signup'))
	elif controller.get_user(username=given_username).password!=given_password:
	 	flash("Password invalid. Please try again.")
	 	return redirect(url_for('login'))

def validate_signup(username, password):
	if controller.get_user(username):
		flash("Username already exists. Please try again.")
		return redirect(url_for('signup'))
