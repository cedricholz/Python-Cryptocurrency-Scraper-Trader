from forex_python.bitcoin import BtcConverter
from Trader.Bittrex3 import Bittrex3
from datetime import datetime, timezone
import urllib
import json
import re
import sys

sys.path.append('../../')


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
    m = re.search('([A-z0-9]+)-([A-z0-9]+)', market)
    return m.group(1)


def get_second_market_coin(market):
    m = re.search('([A-z0-9]+)-([A-z0-9]+)', market)
    return m.group(2)


def get_coin_market_cap_1hr_change():
    coinmarketcap_coins = query_url("https://api.coinmarketcap.com/v1/ticker/?limit=2000")
    d = {}
    for coin in coinmarketcap_coins:
        d[coin['symbol']] = coin['percent_change_1h']
    return d


def get_rank():
    coinmarketcap_coins = query_url("https://api.coinmarketcap.com/v1/ticker/?limit=2000")
    d = {}
    for coin in coinmarketcap_coins:
        d[coin['symbol']] = coin['rank']
    return d


def print_and_write_to_logfile(log_text):
    print(log_text + "\n")
    with open("logs.txt", "a") as myfile:
        myfile.write(log_text + "\n\n")


def get_total_bitcoin(api):
    try:
        return float(api.get_balance('BTC')['result']['Available'])
    except LookupError:
        return 0


def get_date_time():
    now = datetime.now()
    return "%s:%s:%s %s/%s/%s" % (now.hour, now.minute, now.second, now.month, now.day, now.year)


def get_time_passed_minutes(time_opened):
    now = datetime.now()

    time_offset = datetime.utcnow() - now

    try:
        opened_datetime = datetime.strptime(time_opened, "%Y-%m-%dT%H:%M:%S.%f") - time_offset
    except ValueError:
        opened_datetime = datetime.strptime(time_opened, "%Y-%m-%dT%H:%M:%S") - time_offset

    time_diff = now - opened_datetime

    time_passed = time_diff.total_seconds() / 60

    return time_passed


def get_updated_bittrex_coins():
    bittrex_data = query_url("https://bittrex.com/api/v1.1/public/getmarketsummaries")['result']
    coins = {}
    for coin in bittrex_data:
        key = coin['MarketName']
        coins[key] = coin
    return coins


def buy(api, market, amount, coin_price, percent_change_24h, desired_gain, percent_change_1h):
    """
    Makes a buy order and adds the coin to pending_orders
    :param api:
    :param market:
    :param amount:
    :param coin_price:
    :param desired_gain:
    :param percent_change_24h:
    :param percent_change_1h:
    :return:
    """

    total_to_spend = bitcoin_to_USD(coin_price * amount)
    total_to_spend += total_to_spend * 0.0025  # include the fee

    buy_order = api.buy_limit(market, amount, coin_price)

    if buy_order['success']:

        pending_orders = file_to_json("pending_orders.json")
        coin_history = file_to_json("coin_highest_price_history.json")

        coin_price_usd = bitcoin_to_USD(coin_price)
        time = get_date_time()

        print_and_write_to_logfile("BUYING\n" + market + "\n24h%: " + str(
            percent_change_24h) + "\nUSD: $" + str(coin_price_usd) + "\nBTC: " + str(
            coin_price) + "\nAmount: " + str(amount)
                                   + "\nTotal Paid: $" + str(total_to_spend) + "\nTime: " + time + "\n1hr%: " + str(
            percent_change_1h))

        t = {}
        t['market'] = market
        t['highest_24h_change'] = percent_change_24h
        t['original_24h_change'] = percent_change_24h
        t['price_bought'] = coin_price
        t['amount'] = amount
        t['total_paid'] = total_to_spend
        t['sell_threshold'] = 5
        t['uuid'] = buy_order['result']['uuid']
        t['desired_gain'] = desired_gain

        pending_orders['Buying'][market] = t

        s = {}
        s['highest_price_recorded'] = coin_price
        coin_history[market] = s
        json_to_file(coin_history, "coin_highest_price_history.json")

        json_to_file(pending_orders, "pending_orders.json")
    else:
        print_and_write_to_logfile(
            "Buy order of " + str(amount) + " " + market + " did not go through: " + buy_order['message'])
    return buy_order


def sell(api, amount, market, bittrex_coins):
    """
    Makes a sell order and adds the coin to pending_orders
    :param api:
    :param amount:
    :param cur_coin_price:
    :param market:
    :param cur_24h_change:
    :return:
    """

    coin_info = bittrex_coins[market]
    cur_coin_price = float(coin_info['Last'])

    sell_order = api.sell_limit(market, amount, cur_coin_price)
    cur_24h_change = get_percent_change_24h(coin_info)

    held_coins = file_to_json("held_coins.json")
    pending_orders = file_to_json("pending_orders.json")

    if sell_order['success']:
        selling_for = bitcoin_to_USD(cur_coin_price * amount)
        selling_for -= selling_for * 0.0025  # adding the fee for selling

        net_gain_loss = selling_for - float(held_coins[market]['total_paid'])
        cur_coin_price_usd = bitcoin_to_USD(cur_coin_price)
        cur_date_time = get_date_time()

        symbol = get_second_market_coin(market)

        print_and_write_to_logfile(
            "SELLING\n" + str(symbol) + "\nUSD: $" + str(cur_coin_price_usd) + "\nBTC: " + str(
                cur_coin_price) + "\nAmount: " + str(amount)
            + "\n24h%: " + str(cur_24h_change) + "\nTotal Sold For: $" + str(selling_for) + "\nNet Gain/Loss: " + str(
                net_gain_loss) + "\nTime: " + str(cur_date_time))

        t = {}
        t['symbol'] = symbol
        t['cur_coin_price'] = cur_coin_price
        t['cur_coin_price_usd'] = cur_coin_price_usd
        t['amount'] = amount
        t['cur_24h_change'] = cur_24h_change
        t['sold_for'] = selling_for
        t['cur_24h_change'] = cur_24h_change
        t['sold_for'] = selling_for
        t['cur_date_time'] = cur_date_time
        t['cur_24h_change'] = cur_24h_change
        t['uuid'] = sell_order['result']['uuid']
        t['gain'] = net_gain_loss

        pending_orders['Selling'][market] = t
        json_to_file(pending_orders, "pending_orders.json")
    else:
        print_and_write_to_logfile("Sell order did not go through: " + sell_order['message'])


def percent_change(bought_price, cur_price):
    return 100 * (cur_price - bought_price) / bought_price


def init_global_return():
    global_return = file_to_json('global_return.json')
    global_return['Invested'] = 0.0
    global_return['Gain'] = 0.0
    json_to_file(global_return, 'global_return.json')


def delete_entry_from_json(fileName, key):
    temp = file_to_json(fileName)
    del temp[key]
    json_to_file(temp, fileName)
