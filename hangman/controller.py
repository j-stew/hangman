from model import User, Game, Guesses, Word, db

def create_game(user_id):
	game = Game(status='in-progress', user=get_user(user_id))
	db.session.add(game)
	db.session.commit()
	guesses = Guesses(game)
	db.session.add(guesses)
	db.session.commit()
	return game, guesses

def create_user(username, password):
	new_user = User(username, password)
	db.session.add(new_user)
	db.session.commit()

def get_user(given_user):
	if type(given_user)==int:
		return User.query.filter_by(id=given_user).first()
	return User.query.filter_by(username=given_user).first()

def get_game(game_id):
	return Game.query.filter_by(id=game_id).first()

def get_guesses(guesses_id):
	return Guesses.query.filter_by(id=guesses_id).first()

def validate_guess(guess, guesses):
	if len(guess) > 1:
		return 'Please guess a single letter.'
	elif not guess.isalpha():
		return 'Please guess a letter, not punction or numbers.'
	elif guess in guesses.incorrect_guesses or guess in guesses.correct_guesses:
		return '"{}" already guessed. Please guess a new letter.'.format(guess)

def check_guess(guess, guesses):
	guess_lowered=guess.lower()
	guesses.remaining_guesses -= 1
	if guess_lowered in guesses.answer:
		guesses.insert_correct_guess(guess_lowered)
	else:
		guesses.incorrect_guesses += guess_lowered
	db.session.commit()

def update_game(game, guesses, user):
	if "___" not in guesses.correct_guesses:
		game.status='win'
		user.wins += 1
		db.session.commit()
		return 'win'
	elif guesses.remaining_guesses <= 0:
		game.status='loss'
		user.loses += 1
		db.session.commit()
		return 'loss'

def validate_login(username, password):
	if not get_user(username):
		return "Username not found. Please create account.", 'signup'
	elif get_user(username).password!=password:
		return "Password invalid. Please try again.", 'login'

def validate_signup(username, password):
	if get_user(username):
		return "Username already exists. Please try again.", 'signup'
