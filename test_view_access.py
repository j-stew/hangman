import unittest
import os
from string import ascii_lowercase as alphabet, rstrip

import flask

os.environ['DATABASE_URL'] = 'postgres://localhost/test_hangman'

from hangman import hangman_app
from hangman.model import db, Word

hangman_app.config['TESTING']=True

class HangmanAccessTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        db.session.remove()
        db.drop_all()
        db.create_all()
        Word.add_words()

        self.client = hangman_app.test_client()
        data = {'username':'lily_test', 'password':'123_test', 'confirm_password':'123_test'}
        self.client.post('/signup', data=data, follow_redirects=True)

    @classmethod
    def tearDownClass(self):
        db.session.remove()
        db.drop_all()

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
            data = {'username':'invalid', 'password':'invalid', 'confirm_password':'invalid'}
            resp = client.post('/login', data=data, follow_redirects=True)
            self.assertEqual(flask.request.path, '/signup')

    def test_signup_load(self):
        resp = self.client.get('/signup', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_signup_unknown_user_flash(self):
        data = {'username':'invalid', 'password':'invalid'}
        resp = self.client.post('/login', data=data, follow_redirects=True)
        self.assertIn('Username not found', resp.data)

    def test_signup_confirm_password_flash(self):
        data = {'username':'confirm_test', 'password':'123_test', 'confirm_password':'test'}
        resp = self.client.post('/signup', data=data, follow_redirects=True)
        self.assertIn('Passwords do not match', resp.data)

    def test_signup_dupe_username(self):
        data = {'username':'lily_test', 'password':'123_test', 'confirm_password':'123_test'}
        resp = self.client.post('/signup', data=data, follow_redirects=True)
        self.assertIn('Username already exists', resp.data)

    def test_signup_play_redirect(self):
        with hangman_app.test_client() as client:
            data = {'username':'lee_test', 'password':'123_test', 'confirm_password':'123_test'}
            resp = client.post('/signup', data=data, follow_redirects=True)
            path=flask.request.path
            self.assertEqual(path, '/play')

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

if __name__ == '__main__':
    unittest.main()