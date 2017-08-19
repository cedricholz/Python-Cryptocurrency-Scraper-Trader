1. Go to Bittrex and click settings

2. Set up Two-Factor Authentication with Google Authenticator

3. Go to API Keys and add new key, turn on READ INFO, TRADE LIMIT, and TRADE MARKET and put in your authenticator code from Google Authenitcator.

4. Add file, "secrets.json" to file main folder, examples folder, and main folder containing the code below and your key and secret from previous step.
   This file is in the .gitignore so you don't accidentally push your key to the world.

{
  "key": "mykey",
  "secret": "mysecret"
}

5. Test that it works by running bittrex3_tests.py

6. Install pip https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation 

7. Create reddit app to get a client_id and client_secret, hhttps://www.reddit.com/prefs/apps

8. Add file "reddit_secrets.json" to file main folder, examples folder, and main folder containing the code below and your reddit information.

{
  "client_id": "zsdfj34jklkljsdfsfewfefwse",
  "client_secret": "sebt6xscuizxcdfrtsecvcb",
  "password": "waffles",
  "user_agent":"User-Agent: android:com.example.myredditapp:v1.2.3 (by /u/kemitche)",
  "username": "fakebot3"
}

9. Test that it works by running example_reddit_bit.py

Do work in main.py

Libraries to install through with pip and gitbash:

pip install forex-python

pip install praw

Bird, Steven, Edward Loper and Ewan Klein (2009).
Natural Language Processing with Python.  O'Reilly Media Inc.

Python Bittrex Wrapper cloned from https://github.com/ericsomdahl/python-bittrex
