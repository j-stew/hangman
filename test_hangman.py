import unittest
import os
from datetime import datetime

import flask

os.environ['DATABASE_URL'] = 'postgres://localhost/test_hangman'

from hangman import controller, model, hangman_app
hangman_app.config['TESTING']=True

print hangman_app.config['SQLALCHEMY_DATABASE_URI']
print hangman_app.config['SECRET_KEY']
print hangman_app.config['DEBUG']
print hangman_app.config['HOST']
print hangman_app.config['PORT']
print hangman_app.config['TESTING']

class HangmanModelTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        model.db.create_all()
        words = open("hangman/words.txt", "r").read().split("\n")
        for word in words:
            model.db.session.add(model.Word(word))
        model.db.session.commit()

    @classmethod
    def tearDownClass(self):
        model.db.session.remove()
        model.db.drop_all()

    def test_create_word(self):
        self.assertTrue(model.Word.query.count() > 0)

    def test_create_user(self):
        new_user = controller.create_user('jess_test', '123_test')
        user=controller.get_user('jess_test')
        self.assertTrue(user.id > 0)
        self.assertEqual(user.username,'jess_test')
        self.assertEqual(user.password,'123_test')
        self.assertEqual(user.wins, 0)
        self.assertEqual(user.loses, 0)
        self.assertEqual(user.games.count(), 0)

    def test_create_game(self):
        new_user=controller.create_user('lauren_test', '123_test')
        user=controller.get_user('lauren_test')
        game=controller.create_game(user.id)[0]
        self.assertTrue(game.id)
        self.assertTrue(game.created_date < datetime.utcnow())
        self.assertEqual(game.status, 'in-progress')
        self.assertTrue(len(game.answer)>0)
        self.assertTrue(game.guesses.remaining_guesses>0)
        self.assertTrue(game.user_id)

    def test_create_guesses(self):
        new_user=controller.create_user('ryan_test', '789_test')
        user=controller.get_user('ryan_test')
        guesses=controller.create_game(user.id)[1]
        self.assertTrue(guesses.id)
        self.assertTrue(len(guesses.answer)>0)
        self.assertFalse(guesses.correct_guesses.isalpha())
        self.assertFalse(guesses.incorrect_guesses)
        self.assertTrue(guesses.remaining_guesses>0)
        self.assertTrue(guesses.game_id)

class HangmanAccessTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        model.db.session.remove()
        model.db.drop_all()
        model.db.create_all()
        words = open("hangman/words.txt", "r").read().split("\n")
        for word in words:
            model.db.session.add(model.Word(word))
        model.db.session.commit()

    @classmethod
    def tearDownClass(self):
        model.db.session.remove()
        model.db.drop_all()

    def setUp(self):
        self.client = hangman_app.test_client()

    def test_invalid_user(self):
        data = {'username':'invalid', 'password':'invalid'}
        resp = self.client.post('/login', data=data, follow_redirects=True)
        self.assertIn('Username not found', resp.data)

    def test_invalid_password(self):
        data = {'username':'jess_site_test', 'password':'jess_site_test_123'}
        self.client.post('/signup', data=data, follow_redirects=True)

        data = {'username':'jess_site_test', 'password':'invalid'}
        resp = self.client.post('/login', data=data, follow_redirects=True)
        self.assertIn('Password invalid', resp.data)

    def test_protected_page_on_logout(self):
        data = {'username':'lauren_site_test', 'password':'lauren_site_test_123'}
        self.client.post('/signup', data=data, follow_redirects=True)
        login_resp = self.client.get('/play', follow_redirects=True)
        self.assertNotIn('Must login to play', login_resp.data)

        self.client.get('/logout', follow_redirects=True)
        logout_resp = self.client.get('/play', follow_redirects=True)
        self.assertIn('Must login to play', logout_resp.data)

class HangmanPlayTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        model.db.session.remove()
        model.db.drop_all()
        model.db.create_all()
        words = open("hangman/words.txt", "r").read().split("\n")
        for word in words:
            model.db.session.add(model.Word(word))
        model.db.session.commit()

        self.client = hangman_app.test_client()
        data = {'username':'game_test', 'password':'game_test_123'}
        self.client.post('/signup', data=data, follow_redirects=True)

    @classmethod
    def tearDownClass(self):
        model.db.session.remove()
        model.db.drop_all()

    def test_invalid_guess_length(self):
        data = {'guess':'aa'}
        resp = self.client.post('/play', data=data, follow_redirects=True)
        self.assertIn('Please guess a single letter', resp.data)

    def test_invalid_guess_type(self):
        data = {'guess':'1'}
        resp = self.client.post('/play', data=data, follow_redirects=True)
        self.assertIn('not punction or numbers', resp.data)

    def test_invalid_guess_dupe(self):
        data = {'guess':'a'}
        self.client.post('/play', data=data, follow_redirects=True)
        resp = self.client.post('/play', data=data, follow_redirects=True)
        self.assertIn('already guessed', resp.data)

    def test_possible_guesses(self):
        with hangman_app.test_client() as client:
            data = {'username':'game_test', 'password':'game_test_123'}
            client.post('/login', data=data, follow_redirects=True)
            guesses = controller.get_guesses(flask.session['guesses_id'])


            for guess in range(0, guesses.possible_guesses()):
                data = {'guess':'abcdefghijklmnopqrstuvwxyz'[guess]}
                client.post('/play', data=data, follow_redirects=True)

            guesses = controller.get_guesses(flask.session['guesses_id'])
            self.assertEqual(guesses.remaining_guesses, 0)

    def test_mixed_guess_casing(self):
        with hangman_app.test_client() as client:
            data = {'username':'game_test', 'password':'game_test_123'}
            client.post('/login', data=data, follow_redirects=True)
            guesses = controller.get_guesses(flask.session['guesses_id'])


            for guess in range(0, guesses.possible_guesses()):
                data = {'guess':'AbCdEfGhIjKlMnOpQrStUvWxYz'[guess]}
                client.post('/play', data=data, follow_redirects=True)

            guesses = controller.get_guesses(flask.session['guesses_id'])
            self.assertEqual(guesses.remaining_guesses, 0)

    def test_win_loss_redirect(self):
        with hangman_app.test_client() as client:
            data = {'username':'game_test', 'password':'game_test_123'}
            client.post('/login', data=data, follow_redirects=True)
            guesses = controller.get_guesses(flask.session['guesses_id'])


            for guess in range(0, guesses.possible_guesses()):
                data = {'guess':'abcdefghijklmnopqrstuvwxyz'[guess]}
                client.post('/play', data=data, follow_redirects=True)

            path=flask.request.path
            self.assertIn(path, '/win/loss')

    def test_scores_update(self):
        with hangman_app.test_client() as client:
            data = {'username':'game_test', 'password':'game_test_123'}
            client.post('/login', data=data, follow_redirects=True)
            guesses = controller.get_guesses(flask.session['guesses_id'])
            for guess in range(0, guesses.possible_guesses()):
                data = {'guess':'abcdefghijklmnopqrstuvwxyz'[guess]}
                client.post('/play', data=data, follow_redirects=True)

            resp = client.get('/scores', follow_redirects=True)
            user = controller.get_user('game_test')

            self.assertEqual(resp.status, '200 OK')
            self.assertTrue(user.wins > 0 or user.loses > 0)

if __name__ == '__main__':
    unittest.main()
