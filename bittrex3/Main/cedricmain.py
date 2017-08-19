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

# Market to trade at
trade = 'BTC'
currency = 'DOGE'
market = '{0}-{1}'.format(trade, currency)

# Amount of coins to buy
amount = 1500

# How big of a profit you want to make
multiplier = 1.1

# Getting the BTC price for DOGE
dogesummary = api.get_ticker(market)

dogeprice = float(dogesummary['result']['Last'])

print('The price for {0} is {1:.8f} {2}.'.format(currency, dogeprice, trade))

# Buying 1500 DOGE for BTC
print('Buying {0} {1} for {2:.8f} {3}.'.format(amount, currency, dogeprice, trade))
api.buy_limit(market, amount, dogeprice)