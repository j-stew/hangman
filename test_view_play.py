import unittest
import os
from string import ascii_lowercase as alphabet, rstrip

import flask

os.environ['DATABASE_URL'] = 'postgres://localhost/test_hangman'

from hangman import hangman_app
from hangman.model import db, Word
from hangman.controller import create_user, create_game, get_guesses, update_answer, get_game, get_user

hangman_app.config['TESTING']=True

class PlayLoadRedirectTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.create_all()
        Word.add_words()
        cls.client = hangman_app.test_client()
        data = {'username':'lily_test', 'password':'123_test', 'confirm_password':'123_test'}
        cls.client.post('/signup', data=data, follow_redirects=True)

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    def setUp(self):
        data = {'username':'lily_test', 'password':'123_test'}
        self.client.post('/login', data=data, follow_redirects=True)

    def tearDown(self):
        self.client.get('/logout')

    def test_load_play(self):
        resp=self.client.get('/play', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_load_scores(self):
        resp=self.client.get('/scores', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_redirect_play_to_win(self):
        with hangman_app.test_client() as client:
            data = {'username':'lauren_test', 'password':'123_test', 'confirm_password':'123_test'}
            client.post('/signup', data=data, follow_redirects=True)
            answer=get_guesses(flask.session['guesses_id']).answer
            for letter in set(answer):
                resp=client.post('/play', data={'guess':letter}, follow_redirects=True)
            path=flask.request.path
            self.assertEqual(path, '/win')

    def test_redirect_play_to_loss(self):
        with hangman_app.test_client() as client:
            data = {'username':'ryan_test', 'password':'123_test', 'confirm_password':'123_test'}
            client.post('/signup', data=data, follow_redirects=True)
            guesses=get_guesses(flask.session['guesses_id'])
            alphabet_i = 0
            answer_i = 0
            while len(guesses.answer) > answer_i:
                if alphabet[alphabet_i] not in guesses.answer:
                    client.post('/play', data={'guess':alphabet[alphabet_i]}, follow_redirects=True)
                    answer_i += 1
                    alphabet_i += 1
                else:
                    alphabet_i += 1
            path=flask.request.path
            self.assertEqual(path, '/loss')

    def test_new_game_on_login(self):
        with hangman_app.test_client() as client:
            data = {'username':'lily_test', 'password':'123_test'}
            client.post('/login', data=data, follow_redirects=True)
            client.post('/play', data={'guess':'a'}, follow_redirects=True)
            first_game=get_game(flask.session['game_id'])
            client.get('/logout')

            client.post('/login', data=data, follow_redirects=True)
            second_game=get_game(flask.session['game_id'])
            self.assertNotEqual(first_game, second_game)

class PlayFlashTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.create_all()
        Word.add_words()
        cls.client = hangman_app.test_client()
        data = {'username':'lily_test', 'password':'123_test', 'confirm_password':'123_test'}
        cls.client.post('/signup', data=data, follow_redirects=True)

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    def setUp(self):
        data = {'username':'lily_test', 'password':'123_test'}
        self.client.post('/login', data=data, follow_redirects=True)

    def tearDown(self):
        self.client.get('/logout')

    def test_flash_need_single_letter(self):
        data = {'guess':'aa'}
        resp = self.client.post('/play', data=data, follow_redirects=True)
        self.assertIn('Please guess a single letter', resp.data)

    def test_flash_not_punc_or_number(self):
        data = {'guess':'1'}
        resp = self.client.post('/play', data=data, follow_redirects=True)
        self.assertIn('not punctuation or numbers', resp.data)

    def test_flash_already_guessed_letter(self):
        data = {'guess':'a'}
        self.client.post('/play', data=data, follow_redirects=True)
        resp = self.client.post('/play', data=data, follow_redirects=True)
        self.assertIn('already guessed', resp.data)

class PlayGameTest(unittest.TestCase):
    with open("hangman/words.txt", "r+") as f:
        words_full = f.readlines()

    def setUp(self):
        words_short = ''.join(self.words_full[0:5])
        with open("hangman/words.txt", "w") as f:
            f.write(words_short)
        db.create_all()
        Word.add_words()
        self.client = hangman_app.test_client()
        data = {'username':'lily_test', 'password':'123_test', 'confirm_password':'123_test'}
        self.client.post('/signup', data=data, follow_redirects=True)

    def tearDown(self):
        self.client.get('/logout')

        words_full = ''.join(PlayGameTest.words_full)
        with open("hangman/words.txt", "w") as f:
            f.write(words_full)
        db.session.remove()
        db.drop_all()

    def test_answer_cheat(self):
        with hangman_app.test_client() as client:
            data = {'username':'lily_test', 'password':'123_test'}
            client.post('/login', data=data, follow_redirects=True)
            client.post('/play', data={'guess':'a'}, follow_redirects=True)
            client.get('/play', query_string={'answer':'hello'}, follow_redirects=True)
            guesses=get_guesses(flask.session['guesses_id'])
            game=guesses.game

            self.assertEqual(game.answer, 'hello')
            self.assertEqual(guesses.answer, 'hello')
            self.assertEqual(guesses.correct_guesses, '___ ___ ___ ___ ___')
            self.assertEqual(guesses.incorrect_guesses, '')
            self.assertEqual(guesses.remaining_guesses, 5)

    def test_no_repeat_words(self):
        with hangman_app.test_client() as client:
            data = {'username':'repeat_test', 'password':'123_test', 'confirm_password':'123_test'}
            client.post('/signup', data=data)
            i = 1
            total_words = Word.query.count()
            while i <= total_words:
                client.get('/play', follow_redirects=True)
                answer=get_game(flask.session['game_id']).answer
                for letter in set(answer):
                    client.post('/play', data={'guess':letter}, follow_redirects=True)
                i+=1

            user_words = [game.answer for game in get_user(flask.session['user_id']).games]
            all_words = [word.word for word in Word.query.all()]
            self.assertEqual(sorted(user_words), sorted(all_words))

if __name__ == '__main__':
    unittest.main()
