import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import game


class AssetLoadingTests(unittest.TestCase):
    def test_script_directory_is_current_working_directory(self):
        self.assertEqual(os.getcwd(), str(Path(game.__file__).resolve().parent))

    def test_common_assets_are_available_from_the_working_directory(self):
        self.assertTrue(Path("place.png").exists())
        self.assertTrue(Path("enemy.png").exists())


if __name__ == "__main__":
    unittest.main()
