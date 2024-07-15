from ..mocking_helper import mock_imports
from unittest import TestCase

mock_imports(["M145Porter"])



class TestM145Porter(TestCase):
    def test_fzahl(self):
        from qkan.m145porter._import import fzahl

        ret = fzahl(text="")
        self.assertEqual(ret, 0.0)

        ret = fzahl(text="1")
        self.assertEqual(ret, 1.0)

        ret = fzahl(text="1.25")
        self.assertEqual(ret, 1.25)

        with self.assertRaises(BaseException) as err:
            fzahl(text="1.can't to float")
            self.assertIn("1.can't to float", str(err))

        # TODO: Check if this logic is intended.
        ret = fzahl(text="20", n=2)
        self.assertEqual(ret, 0.2)
