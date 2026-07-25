import os
import tempfile
import unittest

from game import TowerDefense


class HighScoreDifficultyTests(unittest.TestCase):
    def setUp(self):
        self.original_home = os.environ.get("HOME")
        self.tempdir = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self.tempdir.name
        self.game = TowerDefense.__new__(TowerDefense)

    def tearDown(self):
        self.tempdir.cleanup()
        if self.original_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = self.original_home

    def test_changing_difficulty_loads_that_difficulty_high_score(self):
        self.game.difficulty = "Easy"
        self.game.high_score = 7
        self.game.save_high_score()

        self.game.difficulty = "Medium"
        self.game.load_high_score()

        self.assertEqual(self.game.high_score, 0)


if __name__ == "__main__":
    unittest.main()
