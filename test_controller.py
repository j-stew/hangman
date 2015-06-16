import unittest
import os
from datetime import datetime
from string import ascii_lowercase as alphabet

os.environ['DATABASE_URL'] = 'postgres://localhost/test_hangman'

from hangman import  model, hangman_app
from hangman.controller import create_game, create_user, validate_login, validate_signup, \
validate_guess, update_guesses, update_game, check_game, get_user

hangman_app.config['TESTING']=True

class Hangmanest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        model.db.session.remove()
        model.db.drop_all()
        model.db.create_all()
        model.Word.add_words()
        user=create_user('lee_test', '123_test')
        game=create_game(user.id)[0]

    @classmethod
    def tearDownClass(cls):
        model.db.session.remove()
        model.db.drop_all()

    def test_username_exists(self):
        self.assertEqual(validate_signup('lee_test', '123_test', '123_test'), 'Username already exists. Please try again.')
        self.assertIsNone(validate_signup('test', '123_test', '123_test'))

    def test_username_not_found(self):
        self.assertEqual(validate_login('lee', '123_test'), ("Username not found. Please create account.", 'signup'))
        self.assertIsNone(validate_login('lee_test', '123_test'))

    def test_password_invalid(self):
        self.assertEqual(validate_login('lee_test', '123'), ("Password invalid. Please try again.", 'login'))

    def test_guess_length(self):
        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        self.assertEqual(validate_guess('aa', guesses), 'Please guess a single letter.')
        self.assertIsNone(validate_guess('a', guesses))

    def test_guess_alpha(self):
        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        self.assertEqual(validate_guess('1', guesses), 'Please guess a letter, not punctuation or numbers.')

    def test_remaining_guess_decrement_when_incorrect(self):
        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        guess=guesses.answer[0]
        update_guesses(guess, guesses)
        self.assertEqual(guesses.remaining_guesses, len(guesses.answer))

        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        for letter in alphabet:
            if not letter in guesses.answer:
                guess=letter
                break
        update_guesses(guess, guesses)
        self.assertEqual(guesses.remaining_guesses, len(guesses.answer)-1)

    def test_remaining_guess_same_when_correct(self):
        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        guess=guesses.answer[0]
        update_guesses(guess, guesses)
        self.assertEqual(guesses.remaining_guesses, len(guesses.answer))

        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        for letter in alphabet:
            if letter in guesses.answer:
                guess=letter
                break
        update_guesses(guess, guesses)
        self.assertEqual(guesses.remaining_guesses, len(guesses.answer))

    def test_guess_not_in_correct(self):
        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        guess=guesses.answer[0]
        update_guesses(guess, guesses)
        self.assertEqual(validate_guess(guess, guesses),
            '"{}" already guessed. Please guess a new letter.'.format(guess))

    def test_guess_not_in_incorrect(self):
        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        for letter in alphabet:
            if not letter in guesses.answer:
                guess=letter
                break

        update_guesses(guess, guesses)
        self.assertEqual(validate_guess(guess, guesses),
            '"{}" already guessed. Please guess a new letter.'.format(guess))

    def test_correct_guess_replace(self):
        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        guess=guesses.answer[0]
        update_guesses(guess, guesses)
        self.assertTrue(any(char.isalpha() for char in guesses.correct_guesses))

    def test_incorrect_guess_without_replace(self):
        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        for letter in alphabet:
            if not letter in guesses.answer:
                guess=letter
                break
        update_guesses(guess, guesses)
        self.assertFalse(any(char.isalpha() for char in guesses.correct_guesses))

    def test_game_check_win(self):
        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        for letter in guesses.answer:
            update_guesses(letter, guesses)
        self.assertTrue(check_game(guesses))

        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        letter=guesses.answer[0]
        update_guesses(letter, guesses)
        self.assertFalse(check_game(guesses))

    def test_game_check_loss(self):
        user=get_user('lee_test')
        guesses=create_game(user.id)[1]
        alphabet_i = 0
        answer_i = 0
        while len(guesses.answer) > answer_i:
            if alphabet[alphabet_i] not in guesses.answer:
                update_guesses(alphabet[alphabet_i], guesses)
                answer_i += 1
                alphabet_i += 1
            else:
                alphabet_i += 1
        update_game(guesses)

        self.assertTrue(check_game(guesses))

    def test_update_game_win(self):
        user=get_user('lee_test')
        user_initial_wins=user.wins
        guesses=create_game(user.id)[1]
        for letter in guesses.answer:
            update_guesses(letter, guesses)
        update_game(guesses)

        self.assertEqual(guesses.game.status, 'win')
        self.assertGreater(user.wins, user_initial_wins)

    def test_update_game_loss(self):
        user=get_user('lee_test')
        user_initial_loses=user.loses
        guesses=create_game(user.id)[1]
        alphabet_i = 0
        answer_i = 0
        while len(guesses.answer) > answer_i:
            if alphabet[alphabet_i] not in guesses.answer:
                update_guesses(alphabet[alphabet_i], guesses)
                answer_i += 1
                alphabet_i += 1
            else:
                alphabet_i += 1
        update_game(guesses)

        self.assertEqual(guesses.game.status, 'loss')
        self.assertGreater(user.loses, user_initial_loses)

if __name__ == '__main__':
    unittest.main()
