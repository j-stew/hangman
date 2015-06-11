# setup client and test_db
# teardown client and test_db
# login
import unittest
import os

import flask

os.environ['DATABASE_URL'] = 'postgres://localhost/test_hangman'

import hangman
hangman.hangman_app.config['TESTING']=True

class HangmanModelTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        hangman.model.db.session.remove()
        hangman.model.db.drop_all()
        hangman.model.db.create_all()
        words = open("hangman/words.txt", "r").read().split("\n")
        for word in words:
            hangman.model.db.session.add(hangman.model.Word(word))
        hangman.model.db.session.commit()

    @classmethod
    def tearDownClass(self):
        hangman.model.db.session.remove()
        hangman.model.db.drop_all()

    def test_word(self):
        self.assertTrue(hangman.model.Word.query.count() > 100)

    def test_user(self):
        new_user = hangman.model.User('jess_test', '123_test')
        hangman.model.db.session.add(new_user)
        hangman.model.db.session.commit()
        self.assertEqual(hangman.model.User.query.filter_by(username='jess_test').first().username,
            'jess_test')

    def test_game(self):
        new_user = hangman.model.User('lauren_test', '456_test')
        hangman.model.db.session.add(new_user)
        hangman.model.db.session.commit()
        new_game = hangman.model.Game(status='in-progress',
            user=hangman.model.User.query.filter_by(username='lauren_test').first())
        hangman.model.db.session.add(new_game)
        hangman.model.db.session.commit()
        self.assertEqual(hangman.model.Game.query.count(), 1)

    def test_guesses(self):
        new_user = hangman.model.User('ryan_test', '789_test')
        hangman.model.db.session.add(new_user)
        hangman.model.db.session.commit()
        new_game = hangman.model.Game(status='in-progress',
            user=hangman.model.User.query.filter_by(username='ryan_test').first())
        hangman.model.db.session.add(new_game)
        hangman.model.db.session.commit()
        new_guesses = hangman.model.Guesses(hangman.model.Game.query.first())
        hangman.model.db.session.add(new_guesses)
        hangman.model.db.session.commit()
        self.assertEqual(hangman.model.Guesses.query.count(), 1)

class HangmanAccessTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        hangman.model.db.session.remove()
        hangman.model.db.drop_all()
        hangman.model.db.create_all()
        words = open("hangman/words.txt", "r").read().split("\n")
        for word in words:
            hangman.model.db.session.add(hangman.model.Word(word))
        hangman.model.db.session.commit()

    @classmethod
    def tearDownClass(self):
        hangman.model.db.session.remove()
        hangman.model.db.drop_all()

    def setUp(self):
        self.client = hangman.hangman_app.test_client()

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

    def test_play_login_protected(self):
        resp = self.client.get('/play', follow_redirects=True)
        self.assertIn('Must login to play', resp.data)

class HangmanPlayTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        hangman.model.db.session.remove()
        hangman.model.db.drop_all()
        hangman.model.db.create_all()
        words = open("hangman/words.txt", "r").read().split("\n")
        for word in words:
            hangman.model.db.session.add(hangman.model.Word(word))
        hangman.model.db.session.commit()

        self.client = hangman.hangman_app.test_client()
        data = {'username':'game_test', 'password':'game_test_123'}
        self.client.post('/signup', data=data, follow_redirects=True)

    @classmethod
    def tearDownClass(self):
        hangman.model.db.session.remove()
        hangman.model.db.drop_all()

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

    def test_test(self):
        with hangman.hangman_app.test_client() as client:
            data = {'username':'game_test', 'password':'game_test_123'}
            client.post('/login', data=data, follow_redirects=True)
            print flask.request.path
            guesses = hangman.controller.get_guesses(flask.session['guesses_id']).possible_guesses()
            
            for guess in range(0, guesses):
                data = 'abcdefghijklmnopqrstuvwxyz'[guess]
                client.post('/play', data=data, follow_redirects=True)
                
            print flask.request.path


if __name__ == '__main__':
    unittest.main()
