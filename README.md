Python Bittrex Wrapper cloned from https://github.com/ericsomdahl/python-bittrex

1. Go to Bittrex and click settings
2. Set up Two-Factor Authentication with Google Authenticator
3. Go to API Keys and add new key, turn on READ INFO, TRADE LIMIT, and TRADE MARKET and put in your authenticator code from Google Authenitcator.

4. Add file, "secrets.json" to file folder containing the code below and your key and secret from previous step.

{
  "key": "mykey",
  "secret": "mysecret"
}
