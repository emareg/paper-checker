import unittest

import re

from papercheck.lib.stripper import stripTeX


class StripperTest(unittest.TestCase):
    def test_stripTeX__tex_only_input__result_has_no_chars(self):
        result = stripTeX(
            "['% document settings\n', '\\documentclass{latex4ei/latex4ei_report}\n', '\n', '\\usepackage{mathptmx} % assumes new font selection scheme installed\n', '\\usepackage{times} % assumes new font selection scheme installed\n', '\\usepackage{amsmath} % assumes amsmath package installed\n', '\\usepackage{amssymb}  % assumes amsmath package installed\n', '\\usepackage{cite}\n', '\\usepackage{hyperref}\n', '\\usepackage{textcomp}\n', '\\usepackage{tikz}\n', '\\usepackage{tabularx}\n', '\\usepackage{multirow}\n', '\\usepackage{caption}\n', '\\usepackage{tikzpeople}\n', '\\usepackage{float}\n', '\\usepackage[utf8]{inputenc}\n', '\\usepackage{marvosym}\n', '\\usepackage{stfloats}\n', '\\usepackage{pgfplots}\n', '\\usepackage{subcaption}\n', '\n', '\\usetikzlibrary{shapes}\n', '\\usetikzlibrary{intersections}\n', '\\usetikzlibrary{calc}\n', '\\usetikzlibrary{optics}\n', '\\usetikzlibrary{arrows}\n', '\\usetikzlibrary{positioning}\n', '\\usetikzlibrary{decorations}\n', '\\usetikzlibrary{angles}\n', '\\usetikzlibrary{quotes}\n', '\\usetikzlibrary{arrows.meta,shapes.geometric,decorations.pathreplacing}\n', '\n', '%\\clearpage\n', '\\addcontentsline{toc}{section}{References}\n', '\\bibliography{references}{}\n', '\\bibliographystyle{plain}\n', '\n', '\\end{document}\n']"
        )
        self.assertIsNone(re.search("[a-zA-Z]", result))


if __name__ == "__main__":
    unittest.main()
