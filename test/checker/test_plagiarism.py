from papercheck.checker.plagiarism import google_search

import unittest


class PlagiarismTest(unittest.TestCase):
    def test_google_search__valid_results(self):
        result = google_search(
            "Their empirical results showed no significant difference between driving based on monitors and using head-mounted displays."
        )
        self.assertTrue(result)
        self.assertTrue(result[0]["title"])
        self.assertTrue(result[0]["url"])
        self.assertTrue(result[0]["desc"])


if __name__ == "__main__":
    unittest.main()
