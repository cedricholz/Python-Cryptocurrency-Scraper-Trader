from bittrex3.bittrex3 import Bittrex3
from forex_python.bitcoin import BtcConverter
import json
import urllib
import requests


with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    secrets_file.close()


api = Bittrex3(secrets['key'], secrets['secret'])


with urllib.request.urlopen("https://api.coinmarketcap.com/v1/ticker/?limit=50") as url:
    coinmarketcap_data = json.loads(url.read().decode())


top_fifty_coins = []


for coin in coinmarketcap_data:
    top_fifty_coins.append(coin['id'])
    
print(top_fifty_coins)