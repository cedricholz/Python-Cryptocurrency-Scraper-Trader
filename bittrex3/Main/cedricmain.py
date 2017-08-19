from bittrex3.bittrex3 import Bittrex3
import json
import time
import urllib


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


with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    secrets_file.close()


api = Bittrex3(secrets['key'], secrets['secret'])

slots_open = 5

trade = 'BTC'

held_coins_file = "held_coins.json"
held_coins = file_to_json(held_coins_file)


while True:
    total_bitcoin = float(api.get_balance('BTC')['result']['Available'])

    with urllib.request.urlopen("https://api.coinmarketcap.com/v1/ticker/?limit=2000") as url:
        coinmarketcap_data = json.loads(url.read().decode())

    #Buying
    if slots_open > 0:
        bitcoin_to_use = float(total_bitcoin/(slots_open + .25))

        for coin in coinmarketcap_data:
            if coin['percent_change_24h']:
                change = float(coin['percent_change_24h'])
                if 40 <= change <= 80:
                    print(coin['symbol'])
                    trade = 'BTC'
                    currency = coin['symbol']
                    market = '{0}-{1}'.format(trade, currency)
                    coin_summary = api.get_ticker(market)

                    if coin_summary['success'] and currency not in held_coins:
                        coin_price = float(coin_summary['result']['Last'])

                        amount = bitcoin_to_use / coin_price

                        print("Would buy this coin, " + currency)

                        if amount > 0:
                            r = api.buy_limit(market, amount, coin_price)

                            if r['success']:
                                slots_open -= 1
                                t = {}
                                t['highest_24h_change'] = coin['percent_change_24h']
                                t['price_bought'] = coin_price
                                t['amount_bought'] = amount

                                held_coins[coin['symbol']] = t

                                json_to_file(held_coins, held_coins_file)

    for cur_coin in coinmarketcap_data:
        cur_symbol = cur_coin['symbol']
        if cur_symbol in held_coins:
            cur_24h_change = float(cur_coin['percent_change_24h'])
            highest_24h_change = float(held_coins[cur_symbol]['highest_24h_change'])

            cur_24h_change = 1

            if cur_24h_change > highest_24h_change:
                held_coins[cur_symbol]['highest_24h_change'] = cur_24h_change
                highest_24h_change = cur_24h_change
                json_to_file(held_coins, held_coins_file)

            if cur_24h_change < highest_24h_change - 10:
                print("Selling " + cur_coin['symbol'])
                trade = 'BTC'
                currency = cur_coin['symbol']
                market = '{0}-{1}'.format(trade, currency)

                cur_coin_summary = api.get_ticker(market)
                cur_coin_price = cur_coin_summary['result']['Last']
                amount = api.get_balance(currency)['result']['Available']

                if amount:
                    if r['success']:
                        slots_open += 1
                        del held_coins[cur_symbol]
                        json_to_file(held_coins, held_coins_file)
                        r = api.sell_limit(market, amount, cur_coin_price)

    time.sleep(10)

