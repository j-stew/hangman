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
		if not session.get('username'):
			flash('Must login to play')
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

def char_replace(guessed, guess, answer):
	guessed = guessed.split(" ")
	char_positions = [i for i, char in enumerate(answer) if char == guess]
	for position in char_positions:
		guessed[position] = guess
	return " ".join(guessed)

def add_game(game_type, guessed, answer, username):
	game = model.Game(game_type, guessed, answer, username)
	model.db.session.add(game)
	user = model.User.query.filter_by(username=session['username']).first()
	if game_type == 'loss':
		user.loses += 1
	else:
		user.wins += 1
	model.db.session.commit()

############
###ROUTES###
############

@hangman_app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'GET':
		return render_template('login.html')

	username = validate_input('username')
	password = validate_input('password')

	user = model.User.query.filter_by(username=username).first()
	if not user:
		flash("Username not found. Please create account.")
		return redirect(url_for('signup'))

	user_password = user.password

	if user_password != password:
	 	flash("Password invalid. Please try again.")
	 	return redirect(url_for('login'))
	else:
		session['username'] = username
		return redirect(url_for('play'))

@hangman_app.route("/signup", methods=["GET", "POST"])
def signup():
	if request.method == 'GET':
		return render_template('signup.html')

	username = validate_input('username')
	password = validate_input('password')

	db_username = model.User.query.filter_by(username=username).first()

	if db_username:
		flash("Username already exists. Please try again.")
		return redirect(url_for('signup'))
	else:
		new_user = model.User(username, password)
		model.db.session.add(new_user)
		model.db.session.commit()
		session['username'] = username
		return redirect(url_for('play'))

@hangman_app.route("/logout", methods=["GET", "POST"])
def logout():
	session.clear()
	return redirect(url_for("login"))

@hangman_app.route("/play", methods=["GET", "POST"])
@auth
def play():
	if not session.get('remaining_guesses') or session.get('remaining_guesses') == 0:
		session['answer'] = random_word()
		session['remaining_guesses'] = session['answer'].possible_guesses
		session['guessed'] = session['answer'].blanks
		session['incorrectly_guessed'] = ''
		session['answer'] = session['answer'].word
		return render_template('play.html', answer=session['answer'], 
			remaining_guesses=session['remaining_guesses'], 
			guessed=session['guessed'], 
			incorrectly_guessed=session['incorrectly_guessed']
			)

	if request.method=='GET':
		return render_template('play.html', answer=session['answer'], 
			remaining_guesses=session['remaining_guesses'], 
			guessed=session['guessed'], 
			incorrectly_guessed=session['incorrectly_guessed']
			)
	
	guess = validate_input('guess').lower()

	if len(guess) > 1:
		flash('Please guess a single letter.')
		return redirect(url_for('play'))

	if guess not in 'abcdefghijklmnopqrstuvwxyz':
		flash('Please guess a letter, not punction or numbers.')
		return redirect(url_for('play'))

	if guess in session['incorrectly_guessed']:
		flash('"{}" already guessed. Please guess a new letter.'.format(guess))
		return redirect(url_for('play'))
		
	# move logic in code below 
		# guess
		# answer 
		# score
			# make the methods from 'verbs'
			# will make adding features easier

	session['remaining_guesses'] -= 1

	if guess in session['answer']:
		session['guessed'] = char_replace(guessed=session['guessed'], guess=guess, answer=session['answer'])
	else:
		session['incorrectly_guessed'] += guess

	if "___" not in session['guessed']:
		add_game('win', session['guessed'], session['answer'], session['username'])
		return redirect(url_for('win'))
	elif session['remaining_guesses'] == 0:
		add_game('loss', session['guessed'], session['answer'], session['username'])
		return redirect(url_for('loss'))
	else:
		return redirect(url_for('play'))

@hangman_app.route("/win")
@auth
def win():
	if "___" in session['guessed']:
		return redirect(url_for('play'))
	return render_template("win.html", answer=session['answer'])

@hangman_app.route("/loss")
@auth
def loss():
	if session.get('remaining_guesses') > 0:
		return redirect(url_for('play'))
	return render_template("loss.html", answer=session['answer'], guessed=session['guessed'])

@hangman_app.route("/scores")
@auth
def scores():
	scores = model.User.query.order_by(model.User.wins.desc()).all()
	top_scores = scores[0:5]
	return render_template("scores.html", top_scores=top_scores)
