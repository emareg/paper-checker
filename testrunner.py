import unittest

if __name__ == "__main__":
    print("Running all unit tests...")
    all_tests = unittest.TestLoader().discover("test")
    unittest.TextTestRunner().run(all_tests)
