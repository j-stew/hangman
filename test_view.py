import unittest
import os
from string import ascii_lowercase as alphabet

import flask

os.environ['DATABASE_URL'] = 'postgres://localhost/test_hangman'

from hangman import model, hangman_app
from hangman.controller import create_user, create_game, get_guesses

hangman_app.config['TESTING']=True

class HangmanAccessTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        model.db.session.remove()
        model.db.drop_all()
        model.db.create_all()
        model.Word.add_words()

        self.client = hangman_app.test_client()
        data = {'username':'lily_test', 'password':'123_test'}
        self.client.post('/signup', data=data, follow_redirects=True)

    @classmethod
    def tearDownClass(self):
        model.db.session.remove()
        model.db.drop_all()

    def test_index_redirect(self):
        with hangman_app.test_client() as client:
            resp=client.get('/', follow_redirects=True)
            self.assertEqual(flask.request.path, '/login')

    def test_login_load(self):
        resp=self.client.get('/', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_login_invalid_password_flash(self):
        data = {'username':'lily_test', 'password':'test'}
        resp = self.client.post('/login', data=data, follow_redirects=True)
        self.assertIn('Password invalid', resp.data)

        data = {'username':'lily_test', 'password':'123_test'}
        resp = self.client.post('/login', data=data, follow_redirects=True)
        self.assertNotIn('Password invalid', resp.data)

    def test_login_unknown_user_flash(self):
        data = {'username':'unknown', 'password':'unknown'}
        resp = self.client.post('/login', data=data, follow_redirects=True)
        self.assertIn('Username not found', resp.data)

    def test_login_unknown_user_signup_redirect(self):
        with hangman_app.test_client() as client:
            data = {'username':'invalid', 'password':'invalid'}
            resp = client.post('/login', data=data, follow_redirects=True)
            self.assertEqual(flask.request.path, '/signup')

    def test_signup_load(self):
        resp = self.client.get('/signup', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_signup_unknown_user_flash(self):
        data = {'username':'invalid', 'password':'invalid'}
        resp = self.client.post('/login', data=data, follow_redirects=True)
        self.assertIn('Username not found', resp.data)

    def test_signup_dupe_username(self):
        data = {'username':'lily_test', 'password':'123_test'}
        resp = self.client.post('/signup', data=data, follow_redirects=True)
        self.assertIn('Username already exists', resp.data)

    def test_signup_play_redirect(self):
        with hangman_app.test_client() as client:
            data = {'username':'lee_test', 'password':'123_test'}
            resp = client.post('/signup', data=data, follow_redirects=True)
            self.assertEqual(flask.request.path, '/play')

    def test_login_play_redirect(self):
        with hangman_app.test_client() as client:
            data = {'username':'lily_test', 'password':'123_test'}
            resp = client.post('/login', data=data, follow_redirects=True)
            self.assertEqual(flask.request.path, '/play')

    def test_logout_login_redirect(self):
        with hangman_app.test_client() as client:
            data = {'username':'lily_test', 'password':'123_test'}
            client.post('/login', data=data, follow_redirects=True)
            client.get('/logout', follow_redirects=True)
            self.assertEqual(flask.request.path, '/login')

    def test_protected_page_after_logout(self):
        data = {'username':'lily_test', 'password':'123_test'}
        self.client.post('/login', data=data, follow_redirects=True)
        self.client.get('/logout', follow_redirects=True)
        resp = self.client.get('/play', follow_redirects=True)
        self.assertIn('Must login to play', resp.data)

class HangmanPlayTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        model.db.session.remove()
        model.db.drop_all()
        model.db.create_all()
        model.Word.add_words()

        self.client = hangman_app.test_client()
        data = {'username':'lily_test', 'password':'123_test'}
        self.client.post('/signup', data=data, follow_redirects=True)

    @classmethod
    def tearDownClass(self):
        model.db.session.remove()
        model.db.drop_all()

    def setUp(self):
        data = {'username':'lily_test', 'password':'123_test'}
        self.client.post('/login', data=data, follow_redirects=True)

    def tearDown(self):
        self.client.get('/logout')

    def test_game_does_not_persist_after_logout(self):
        with hangman_app.test_client() as client:
            data = {'username':'lily_test', 'password':'123_test'}
            client.post('/login', data=data, follow_redirects=True)
            client.post('/play', data={'guess':'a'}, follow_redirects=True)
            client.get('/logout')

            data = {'username':'lily_test', 'password':'123_test'}
            resp=client.post('/login', data=data, follow_redirects=True)

    def test_play_load(self):
        resp=self.client.get('/play', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_scores_load(self):
        resp=self.client.get('/scores', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_play_guess_length_flash(self):
        data = {'guess':'aa'}
        resp = self.client.post('/play', data=data, follow_redirects=True)
        self.assertIn('Please guess a single letter', resp.data)

    def test_play_guess_alpha_flash(self):
        data = {'guess':'1'}
        resp = self.client.post('/play', data=data, follow_redirects=True)
        self.assertIn('not punction or numbers', resp.data)

    def test_play_guess_dupe_flash(self):
        data = {'guess':'a'}
        self.client.post('/play', data=data, follow_redirects=True)
        resp = self.client.post('/play', data=data, follow_redirects=True)
        self.assertIn('already guessed', resp.data)

    # def test_win_redirect(self):
    #     with hangman_app.test_client() as client:
    #         data = {'username':'lauren_test', 'password':'123_test'}
    #         client.post('/signup', data=data, follow_redirects=True)
    #         answer=get_guesses(flask.session['guesses_id']).answer
    #         for letter in answer:
    #             client.post('/play', data={'guess':letter}, follow_redirects=True)
    #             path=flask.request.path
    #             print path
    #         self.assertEqual(path, '/win')

    def test_loss_redirect(self):
        with hangman_app.test_client() as client:
            data = {'username':'ryan_test', 'password':'123_test'}
            client.post('/signup', data=data, follow_redirects=True)
            answer=get_guesses(flask.session['guesses_id']).answer
            alphabet_i = 0
            answer_i = 0
            while len(answer) > answer_i:
                if answer[answer_i] != alphabet[alphabet_i]:
                    client.post('/play', data={'guess':alphabet[alphabet_i]}, follow_redirects=True)
                    answer_i += 1
                else:
                    alphabet_i += 1
            path=flask.request.path
            self.assertEqual(path, '/loss')

if __name__ == '__main__':
    unittest.main()