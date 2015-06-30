import unittest
import os
from string import ascii_lowercase as alphabet, rstrip

import flask

os.environ['DATABASE_URL'] = 'postgres://localhost/test_hangman'

from hangman import hangman_app
from hangman.model import db, Word

hangman_app.config['TESTING']=True

class AccessLoadRedirectTest(unittest.TestCase):
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

    def test_load_login(self):
        resp=self.client.get('/', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_load_signup(self):
        resp = self.client.get('/signup', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_redirect_index_to_login(self):
        with hangman_app.test_client() as client:
            resp=client.get('/', follow_redirects=True)
            self.assertEqual(flask.request.path, '/login')

    def test_redirect_login_to_signup(self):
        with hangman_app.test_client() as client:
            data = {'username':'invalid', 'password':'invalid', 'confirm_password':'invalid'}
            resp = client.post('/login', data=data, follow_redirects=True)
            self.assertEqual(flask.request.path, '/signup')

    def test_redirect_signup_to_play(self):
        with hangman_app.test_client() as client:
            data = {'username':'lee_test', 'password':'123_test', 'confirm_password':'123_test'}
            resp = client.post('/signup', data=data, follow_redirects=True)
            path=flask.request.path
            self.assertEqual(path, '/play')

    def test_redirect_login_to_play(self):
        with hangman_app.test_client() as client:
            data = {'username':'lily_test', 'password':'123_test'}
            resp = client.post('/login', data=data, follow_redirects=True)
            self.assertEqual(flask.request.path, '/play')

    def test_redirect_logout_to_login(self):
        with hangman_app.test_client() as client:
            data = {'username':'lily_test', 'password':'123_test'}
            client.post('/login', data=data, follow_redirects=True)
            client.get('/logout', follow_redirects=True)
            self.assertEqual(flask.request.path, '/login')

class AccessFlashTest(unittest.TestCase):
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

    def test_flash_invalid_password_on_login(self):
        data = {'username':'lily_test', 'password':'test'}
        resp = self.client.post('/login', data=data, follow_redirects=True)
        self.assertIn('Password invalid', resp.data)

        data = {'username':'lily_test', 'password':'123_test'}
        resp = self.client.post('/login', data=data, follow_redirects=True)
        self.assertNotIn('Password invalid', resp.data)

    def test_flash_unknown_user_on_login(self):
        data = {'username':'unknown', 'password':'unknown'}
        resp = self.client.post('/login', data=data, follow_redirects=True)
        self.assertIn('Username not found', resp.data)

    def test_flash_confirm_password_on_signup(self):
        data = {'username':'confirm_test', 'password':'123_test', 'confirm_password':'test'}
        resp = self.client.post('/signup', data=data, follow_redirects=True)
        self.assertIn('Passwords do not match', resp.data)

    def test_flash_duplicate_username_on_signup(self):
        data = {'username':'lily_test', 'password':'123_test', 'confirm_password':'123_test'}
        resp = self.client.post('/signup', data=data, follow_redirects=True)
        self.assertIn('Username already exists', resp.data)

    def test_flash_must_login_after_logout(self):
        data = {'username':'lily_test', 'password':'123_test'}
        self.client.post('/login', data=data, follow_redirects=True)
        self.client.get('/logout', follow_redirects=True)
        resp = self.client.get('/play', follow_redirects=True)
        self.assertIn('Must login to play', resp.data)

if __name__ == '__main__':
    unittest.main()
