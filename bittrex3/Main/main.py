from bittrex3.bittrex3 import Bittrex3
import json
import urllib

with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    secrets_file.close()


api = Bittrex3(secrets['key'], secrets['secret'])


with urllib.request.urlopen("https://api.coinmarketcap.com/v1/ticker/?limit=1000") as url:
    coinmarketcap_data = json.loads(url.read().decode())

top_coins = []

for coin in coinmarketcap_data:
    top_coins.append(coin['id'])

