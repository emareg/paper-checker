import unittest

from papercheck.textstats import createStats


class TextStatsTest(unittest.TestCase):
    def test_createStats__words_count_zero__valid_result(self):
        result = createStats("\n\n\n\n\n")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
