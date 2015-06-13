import unittest
import os
from datetime import datetime

os.environ['DATABASE_URL'] = 'postgres://localhost/test_hangman'

from hangman import controller, model, hangman_app
hangman_app.config['TESTING']=True

class HangmanModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        model.db.session.remove()
        model.db.drop_all()
        model.db.create_all()
        model.Word.add_words()

    @classmethod
    def tearDownClass(cls):
        model.db.session.remove()
        model.db.drop_all()

    def test_create_word(self):
        self.assertTrue(model.Word.query.count() > 0)

    def test_create_get_user(self):
        new_user = controller.create_user('jess_test', '123_test')
        user=controller.get_user('jess_test')
        self.assertTrue(user.id > 0)
        self.assertEqual(user.username,'jess_test')
        self.assertEqual(user.password,'123_test')
        self.assertEqual(user.wins, 0)
        self.assertEqual(user.loses, 0)
        self.assertEqual(user.games.count(), 0)

    def test_create_get_game(self):
        new_user=controller.create_user('lauren_test', '123_test')
        user=controller.get_user('lauren_test')
        game=controller.create_game(user.id)[0]
        self.assertTrue(game.id)
        self.assertTrue(game.created_date < datetime.utcnow())
        self.assertEqual(game.status, 'in-progress')
        self.assertTrue(len(game.answer)>0)
        self.assertTrue(game.guesses.remaining_guesses>0)
        self.assertTrue(game.user_id)

    def test_create_get_guesses(self):
        new_user=controller.create_user('ryan_test', '789_test')
        user=controller.get_user('ryan_test')
        guesses=controller.create_game(user.id)[1]
        self.assertTrue(guesses.id)
        self.assertTrue(len(guesses.answer)>0)
        self.assertFalse(guesses.correct_guesses.isalpha())
        self.assertFalse(guesses.incorrect_guesses)
        self.assertTrue(guesses.remaining_guesses>0)
        self.assertTrue(guesses.game_id)

if __name__ == '__main__':
    unittest.main()
