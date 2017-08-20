from forex_python.bitcoin import BtcConverter
from bittrex3.bittrex3 import Bittrex3
import urllib
import json
import re

def file_to_json(filename):
    try:
        file = open(filename, 'r')
        contents = str(file.read())
        posts = json.loads(contents)
        file.close()
        return posts
    except FileNotFoundError:
        print("No such file: " + filename)
        exit(1)


def json_to_file(json_obj, filename):
    try:
        file = open(filename, 'w')
        json.dump(json_obj, file, sort_keys=True, indent=4, separators=(',', ': '))
        file.close()
    except FileNotFoundError:
        print("No such file: " + filename)
        exit(1)


def get_percent_change_24h(coin):
    return (coin['Last'] / coin['PrevDay'] - 1) * 100


def bitcoin_to_USD(bitcoin_amount):
    b = BtcConverter()
    latest_price = b.get_latest_price('USD')
    return latest_price * bitcoin_amount


def get_api():
    with open("secrets.json") as secrets_file:
        secrets = json.load(secrets_file)
        secrets_file.close()

    return Bittrex3(secrets['key'], secrets['secret'])

def query_url(url_addr):
    with urllib.request.urlopen(url_addr) as url:
        return json.loads(url.read().decode())


def get_first_market_coin(market):
    m = re.search('([A-z]+)-([A-z]+)', market)
    return m.group(1)

def get_second_market_coin(market):
    m = re.search('([A-z]+)-([A-z]+)', market)
    return m.group(2)

def get_coin_market_cap_1hr_change():
    coinmarketcap_coins = query_url("https://api.coinmarketcap.com/v1/ticker/?limit=2000")
    d = {}
    for coin in coinmarketcap_coins:
        d[coin['symbol']] = coin['percent_change_1h']
    return d