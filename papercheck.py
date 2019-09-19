# this is a wrapper script for calling the __main__.py under ./src

import sys
sys.path.append("./src")
import src.__main__
