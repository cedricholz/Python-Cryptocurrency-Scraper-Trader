1. Go to Bittrex and click settings

2. Set up Two-Factor Authentication with Google Authenticator

3. Go to API Keys and add new key, turn on READ INFO, TRADE LIMIT, and TRADE MARKET and put in your authenticator code from Google Authenitcator.

4. Add file, "secrets.json" to file Trader folder, examples folder, and Main folder containing the code below and your key and secret from previous step.
   This file is in the .gitignore so you don't accidentally push your key to the world.

{
  "key": "mykey",
  "secret": "mysecret"
}

5. Test that it works by running bittrex3_tests.py

6. Install pip https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation 

7. Create reddit app here, https://www.reddit.com/prefs/apps. Scroll down to the bottom and click create an app. Give it whatever name you want, click script, no description or about url necessary, for redirect url put http://127.0.0.1.

client_id is the string under personal use script

client_secret is the string next to secret

8. Add file "reddit_secrets.json" to file main folder, examples folder, and main folder containing the code below and your reddit information.

{
  "client_id": "zsdfj34jklkljsdfsfewfefwse",
  "client_secret": "sebt6xscuizxcdfrtsecvcb",
  "password": "waffles",
  "user_agent":"User-Agent: android:com.example.myredditapp:v1.2.3 (by /u/kemitche)",
  "username": "fakebot3"
}

9. Test that it works by running example_reddit_bit.py

10. In Main create new several files called held_coins.json, coin_highest_price_history.json, global_return.json, keltner_coins.json, reddit_coins.json and fill it with {}

11. In Main create a new file called pending_orders.json and fill it with this

{
    "Buying": {
    },
    "Selling": {}
}


12. Add file "email_info.json" to Main and fill it with your info
{
  "email_address": "myaddress",
  "password": "mypassword"
}

Libraries to install through with pip and gitbash:

pip install forex-python

pip install praw

Bird, Steven, Edward Loper and Ewan Klein (2009).
Natural Language Processing with Python.  O'Reilly Media Inc.

Python Bittrex Wrapper cloned from https://github.com/ericsomdahl/python-bittrex
