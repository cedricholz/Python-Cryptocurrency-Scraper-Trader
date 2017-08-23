import unittest
import json
from Trader.Bittrex3 import Bittrex3


def test_basic_response(unit_test, result, method_name):
    unit_test.assertTrue(result['success'], "{0:s} failed".format(method_name))
    unit_test.assertTrue(result['message'] is not None, "message not present in response")
    unit_test.assertTrue(result['result'] is not None, "result not present in response")


def test_auth_basic_failures(unit_test, result, test_type):
    unit_test.assertFalse(result['success'], "{0:s} failed".format(test_type))
    unit_test.assertTrue('invalid' in str(result['message']).lower(), "{0:s} failed response message".format(test_type))
    unit_test.assertIsNone(result['result'], "{0:s} failed response result not None".format(test_type))


class TestBittrex3PublicAPI(unittest.TestCase):
    """
    Integration tests for the Bittrex3 public API.
    These will fail in the absence of an internet connection or if bittrex3 API goes down
    """

    def setUp(self):
        self.bittrex = Bittrex3(None, None)

    def test_handles_none_key_or_secret(self):
        self.bittrex = Bittrex3(None, None)
        # could call any public method here
        actual = self.bittrex.get_markets()
        self.assertTrue(actual['success'], "failed with None key and None secret")

        self.bittrex = Bittrex3("123", None)
        actual = self.bittrex.get_markets()
        self.assertTrue(actual['success'], "failed with None secret")

        self.bittrex = Bittrex3(None, "123")
        self.assertTrue(actual['success'], "failed with None key")

    def test_get_markets(self):
        actual = self.bittrex.get_markets()
        test_basic_response(self, actual, "get_markets")
        self.assertTrue(isinstance(actual['result'], list), "result is not a list")
        self.assertTrue(len(actual['result']) > 0, "result list is 0-length")

    def test_get_currencies(self):
        actual = self.bittrex.get_currencies()
        test_basic_response(self, actual, "get_currencies")
        pass


class TestBittrex3AccountAPI(unittest.TestCase):
    """
    Integration tests for the Bittrex3 Account API.
      * These will fail in the absence of an internet connection or if bittrex3 API goes down.
      * They require a valid API key and secret issued by Bittrex3.
      * They also require the presence of a JSON file called secrets.json.
      It is structured as such:
    {
      "key": "12341253456345",
      "secret": "3345745634234534"
    }
    """

    def setUp(self):
        with open("secrets.json") as secrets_file:
            self.secrets = json.load(secrets_file)
            secrets_file.close()
        self.bittrex = Bittrex3(self.secrets['key'], self.secrets['secret'])

    def test_handles_invalid_key_or_secret(self):
        self.bittrex = Bittrex3('invalidkey', self.secrets['secret'])
        actual = self.bittrex.get_balance('BTC')
        test_auth_basic_failures(self, actual, 'Invalid key, valid secret')

        self.bittrex = Bittrex3(None, self.secrets['secret'])
        actual = self.bittrex.get_balance('BTC')
        test_auth_basic_failures(self, actual, 'None key, valid secret')

        self.bittrex = Bittrex3(self.secrets['key'], 'invalidsecret')
        actual = self.bittrex.get_balance('BTC')
        test_auth_basic_failures(self, actual, 'valid key, invalid secret')

        self.bittrex = Bittrex3(self.secrets['key'], None)
        actual = self.bittrex.get_balance('BTC')
        test_auth_basic_failures(self, actual, 'valid key, None secret')

        self.bittrex = Bittrex3('invalidkey', 'invalidsecret')
        actual = self.bittrex.get_balance('BTC')
        test_auth_basic_failures(self, actual, 'invalid key, invalid secret')
        pass

    def test_get_balance(self):
        actual = self.bittrex.get_balance('BTC')
        test_basic_response(self, actual, "getbalance")
        self.assertTrue(isinstance(actual['result'], dict), "result is not a dict")
        self.assertEqual(actual['result']['Currency'],
                         "BTC",
                         "requested currency {0:s} does not match returned currency {1:s}"
                         .format("BTC", actual['result']['Currency']))


if __name__ == '__main__':
    unittest.main()
