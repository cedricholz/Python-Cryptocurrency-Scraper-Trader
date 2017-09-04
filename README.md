1. Go to Bittrex and click settings

2. Set up Two-Factor Authentication with Google Authenticator

3. Go to API Keys and add new key, turn on 
```
READ INFO, TRADE LIMIT, and TRADE MARKET
```
and put in your authenticator code from Google Authenticator to get your key and secret key.

4. Add file, "secrets.json" to file Trader folder, examples folder, and Main folder containing the code below and your key and secret from previous step. All files to add are in the git ignore so we don't push our secrets.

```
{
  "key": "mykey",
  "secret": "mysecret"
}
```

5. Test that it works by running bittrex3_tests.py

6. Create reddit app here, https://www.reddit.com/prefs/apps. Scroll down to the bottom and click create an app. Give it whatever name you want, click script, no description or about url necessary, for redirect url put http://www.example.com/unused/redirect/uri.

client_id is the string under personal use script

client_secret is the string next to secret
![alt text](https://github.com/cedricholz/Python-Cryptocurrency-Scraper-Trader/blob/master/Trader/reddit_ids.png "Logo Title Text 1")

7. Add file "reddit_secrets.json" to file main folder, examples folder, and main folder containing the code below and your reddit information.

```python
{
  "client_id": "zsdfj34jklkljsdfsfewfefwse",
  "client_secret": "sebt6xscuizxcdfrtsecvcb",
  "password": "waffles",
  "user_agent":"User-Agent: android:com.example.myredditapp:v1.2.3 (by /u/kemitche)",
  "username": "fakebot3"
}
```

8. Test that it works by running example_reddit_bot.py

9. In Main create new several files called held_coins.json, coin_highest_price_history.json, global_return.json, keltner_coins.json, reddit_coins.json and fill them with 

```python
{}
```

10. In Main create a new file called pending_orders.json and fill it with this

```python
{
    "Buying": {
    },
    "Selling": {}
}
```


11. Add file "email_info.json" to Main and fill it with your gmail account info

```python
{
  "email_address": "myaddress",
  "password": "mypassword",
  "recipiant_emails" : ["myaddress","anotheremailaddress"]
}
```

12. Add file "coins_to_dismiss.json" and fill it with this

```python
{
  "established_coins":  ["ETH", "BTC"],
  "coins_with_common_names" : ["TIME", "START","OMG","NEO", "RISE", "PAY", "STRAT","FUN","TRUST", "SHIFT"],
  "coins_already_profited_on" :[]
}
```

13. Install gitbash if you have windows, otherwise use your terminal https://git-scm.com/downloads

14. Install pip https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation 

Libraries to install through with pip and through gitbash or terminal:

```python
pip3 install forex-python

pip3 install praw
```



>Bird, Steven, Edward Loper and Ewan Klein (2009).
>Natural Language Processing with Python.  O'Reilly Media Inc.

>Python Bittrex Wrapper cloned from https://github.com/ericsomdahl/python-bittrex
