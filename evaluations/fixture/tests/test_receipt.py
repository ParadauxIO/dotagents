import unittest

from receipt import preview, receipt


class ReceiptTests(unittest.TestCase):
    def test_default_tax(self):
        self.assertEqual(receipt([1000]), "Total: $12.00")
        self.assertEqual(preview([1000]), {"amount_cents": 1200})
