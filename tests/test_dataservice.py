import unittest

from app.data import DataDomain

class TestDataDomain(unittest.TestCase):
    def test_datadomain(self) -> None:
        self.assertEqual(DataDomain.from_str('beeldbank'), DataDomain.BeeldBank)
        self.assertEqual(DataDomain.from_str('BEELDBANK'), DataDomain.BeeldBank)
        self.assertEqual(DataDomain.from_str('BEELDbank'), DataDomain.BeeldBank)
        self.assertIsNone(DataDomain.from_str('does not exist'))

        self.assertEqual(DataDomain.from_str('str'), None)
        self.assertEqual(DataDomain.from_str('Foobar'), None)


