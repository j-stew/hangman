# setup client and test_db
# teardown client and test_db
# login
import unittest
import os

os.environ['DATABASE_URL'] = 'postgres://localhost/test_hangman'

import hangman

class HangmanTest(unittest.TestCase):

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

if __name__ == '__main__':
    unittest.main()
