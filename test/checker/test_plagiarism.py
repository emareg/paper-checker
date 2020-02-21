from papercheck.checker.plagiarism import google_search

import unittest


class PlagiarismTest(unittest.TestCase):
    def test_google_search(self):
        google_search(
            "Their empirical results showed no significant difference between driving based on monitors and using head-mounted displays."
        )
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
