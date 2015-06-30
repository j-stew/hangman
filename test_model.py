import unittest
import os
from datetime import datetime
from string import rstrip

os.environ['DATABASE_URL'] = 'postgres://localhost/test_hangman'

from hangman.model import db, Word
from hangman import hangman_app, model, controller
hangman_app.config['TESTING']=True

class ModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.create_all()
        Word.add_words()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    def test_words_added(self):
        self.assertTrue(Word.query.count() > 100)

    def test_user_fields(self):
        new_user = controller.create_user('jess_test', '123_test')
        user=controller.get_user('jess_test')
        self.assertTrue(user.id > 0)
        self.assertEqual(user.username,'jess_test')
        self.assertEqual(user.password,'123_test')
        self.assertEqual(user.wins, 0)
        self.assertEqual(user.loses, 0)
        self.assertEqual(user.games.count(), 0)

    def test_game_fields(self):
        new_user=controller.create_user('lauren_test', '123_test')
        user=controller.get_user('lauren_test')
        game=controller.create_game(user.id)[0]
        self.assertTrue(game.id)
        self.assertTrue(game.created_date < datetime.utcnow())
        self.assertEqual(game.status, 'in-progress')
        self.assertTrue(len(game.answer)>0)
        self.assertTrue(game.guesses.remaining_guesses>0)
        self.assertTrue(game.user_id)

    def test_guesses_fields(self):
        new_user=controller.create_user('ryan_test', '789_test')
        user=controller.get_user('ryan_test')
        guesses=controller.create_game(user.id)[1]
        self.assertTrue(guesses.id)
        self.assertTrue(len(guesses.answer)>0)
        self.assertFalse(guesses.correct_guesses.isalpha())
        self.assertFalse(guesses.incorrect_guesses)
        self.assertTrue(guesses.remaining_guesses>0)
        self.assertTrue(guesses.game_id)

class WordFileTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.create_all()
        Word.add_words()

    @classmethod
    def tearDownClass(cls):
        """Removes text added to file during test"""
        db.session.remove()
        db.drop_all()

        with open("hangman/words.txt", "r+") as f:
            words = f.read()
            words = rstrip(words, '\ntest_add_words')

        with open("hangman/words.txt", "w") as f:
            f.write(words)

    def test_file_edit_adds_word(self):
        with open("hangman/words.txt", "a") as f:
            f.write("\ntest_add_words")

        Word.add_words()
        last_added_word = Word.query.order_by(Word.added_date.desc()).first().word
        self.assertEqual(last_added_word, "test_add_words")

if __name__ == '__main__':
    unittest.main()
