#!/usr/bin/env python
# This program buys some Dogecoins and sells them for a bigger price

import sys
sys.path.append('../../')

from Trader.Bittrex3 import Bittrex3
from forex_python.bitcoin import BtcConverter
import json

b = BtcConverter()

latestBitcoinPrice = b.get_latest_price('USD')
print("Latest Bitcoin Price " + str(latestBitcoinPrice))

dollarsToUSD = b.convert_to_btc(1, "USD")
print("1 USD to bitcoin " + str(dollarsToUSD))


def bitcoin_to_USD(amount):
    b = BtcConverter()
    latest_price = b.get_latest_price('USD')
    return latest_price * amount


print(bitcoin_to_USD(0.00122808))

# Get these from https://bittrex.com/Account/ManageApiKey

with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    secrets_file.close()

api = Bittrex3(secrets['key'], secrets['secret'])

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

r = api.buy_limit(market, amount, dogeprice)

# Multiplying the price by the multiplier
# dogeprice = round(dogeprice*multiplier, 8)
dogeprice = round(dogeprice * 1.1, 8)

# Selling 1500 DOGE for the  new price
print('Selling {0} {1} for {2:.8f} {3}.'.format(amount, currency, dogeprice, trade))
r = api.sell_limit(market, amount, dogeprice)

# Gets the DOGE balance
dogebalance = api.get_balance(currency)
print("Your balance is {0} {1}.".format(dogebalance['result']['Balance'], currency))

# For a full list of functions, check out bittrex.py or https://bittrex.com/Home/Api
