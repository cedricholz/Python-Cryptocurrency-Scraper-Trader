Python Bittrex Wrapper cloned from https://github.com/ericsomdahl/python-bittrex

1. Go to Bittrex and click settings

2. Set up Two-Factor Authentication with Google Authenticator

3. Go to API Keys and add new key, turn on READ INFO, TRADE LIMIT, and TRADE MARKET and put in your authenticator code from Google Authenitcator.

4. Add file, "secrets.json" to file main folder and the test folder containing the code below and your key and secret from previous step.
   This file is in the .gitignore so you don't accidentally push your key to the world.

{
  "key": "mykey",
  "secret": "mysecret"
}

5. Test that it works by running bittrex3_tests.py

6. Do work in script.py

7. Install pip https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation


Libraries to install through with pip and gitbash:

pip install forex-python
