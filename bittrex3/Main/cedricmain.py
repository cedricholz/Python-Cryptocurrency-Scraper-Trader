import bittrex3.utils as utils
import time


def buy(market, amount, coin_price, percent_change_24h):
    buy_order = api.buy_limit(market, amount, coin_price)
    if buy_order['success']:
        total_paid = utils.bitcoin_to_USD(coin_price * amount)
        coin_price_usd = utils.bitcoin_to_USD(coin_price)
        utils.print_and_write_to_logfile("Bought " + str(amount) + " of " + str(market) + " at BTC " + str(
            coin_price) + ", $" + coin_price_usd + ", " + "with 24h Gain of " + percent_change_24h
                + "%, Total Paid: $" + str(total_paid)) + " Time: " + utils.get_date_time()

        t = {}
        t['highest_24h_change'] = percent_change_24h
        t['original_24h_change'] = percent_change_24h
        t['price_bought'] = coin_price
        t['amount_bought'] = amount
        t['total_paid'] = total_paid
        t['sell_threshold'] = 10

        held_coins[market] = t

        utils.json_to_file(held_coins, "held_coins.json")
    else:
        utils.print_and_write_to_logfile("Buy order did not go through: " + buy_order['message'])


def find_and_buy(total_bitcoin):

    bittrex_coins = utils.query_url("https://bittrex.com/api/v1.1/public/getmarketsummaries")['result']

    symbol_1h_change_pairs = utils.get_coin_market_cap_1hr_change()

    for coin in bittrex_coins:
        slots_open = 5 - len(held_coins)
        if slots_open <= 0:
            break
        percent_change_24h = utils.get_percent_change_24h(coin)
        if buy_min_percent <= percent_change_24h <= buy_max_percent:
            market = coin['MarketName']
            if market.startswith('ETH'):
                break
            if market.startswith('BTC'):
                coin_summary = api.get_ticker(market)
                if coin_summary['success']:
                    coin_to_buy = utils.get_second_market_coin(market)
                    coin_1h_change = float(symbol_1h_change_pairs[coin_to_buy])
                    if market not in held_coins and coin_1h_change > buy_desired_1h_change:
                        bitcoin_to_use = float(total_bitcoin / (slots_open + .25))
                        coin_price = float(coin_summary['result']['Last'])
                        amount = bitcoin_to_use / coin_price
                        if amount > 0:
                            buy(market, amount, coin_price, percent_change_24h)
                else:
                    utils.print_and_write_to_logfile("Could not obtain coin summary :" + coin_summary['message'])


def updated_threshold(market, coins):
    coin = coins[market]
    original_24h_change = coin['original_24h_change']
    h = coin['highest_24h_change']
    cur_threshold = coin['sell_threshold']
    total_change = h - original_24h_change
    return 10
    # if h <= 40:
    #     return 10
    # if h >= 100:
    #     return 30
    # if 40 < h <= 50:
    #     return 10
    # if 50 <= h <= 60:
    #     return 13
    # if 60 <= h <= 70:
    #     return 14
    # if 70 <= h <= 80:
    #     return 20
    # if 80 <= h <= 90:
    #     return 23
    # if 90 <= h < 100:
    #     return 25


def sell(amount, coin_to_sell, cur_coin_price, coin_market, cur_24h_change):
    sell_order = api.sell_limit(coin_market, amount, cur_coin_price)
    if sell_order['success']:
        sold_for = utils.bitcoin_to_USD(cur_coin_price * amount)
        net_gain_loss = sold_for - float(held_coins[coin_market]['total_paid'])
        cur_coin_price_usd = utils.bitcoin_to_USD(cur_coin_price)

        utils.print_and_write_to_logfile("Sold " + str(amount) + " of " + str(coin_to_sell) + " at BTC " + str(
            cur_coin_price) + ", $" + str(cur_coin_price_usd) + ", " + "with 24h Gain of " + str(cur_24h_change) + "%, Total Sold For: $" + str(
            sold_for))
        + " with net gain/loss: $" + str(net_gain_loss) + " Time: " + utils.get_date_time()

        del held_coins[coin_market]
        utils.json_to_file(held_coins, "held_coins.json")
    else:
        utils.print_and_write_to_logfile("Sell order did not go through: " + sell_order['message'])


def update_and_or_sell():
    held_markets = [market for market in held_coins]
    for coin_market in held_markets:
        coin_info = utils.query_url("https://bittrex.com/api/v1.1/public/getmarketsummary?market=" + coin_market)['result'][0]

        cur_24h_change = utils.get_percent_change_24h(coin_info)
        highest_24h_change = held_coins[coin_market]['highest_24h_change']

        if cur_24h_change > highest_24h_change:
            held_coins[coin_market]['highest_24h_change'] = cur_24h_change
            highest_24h_change = cur_24h_change
            utils.json_to_file(held_coins, "held_coins.json")

        held_coins[coin_market]['sell_threshold'] = updated_threshold(coin_market, held_coins)
        utils.json_to_file(held_coins, "held_coins.json")

        if cur_24h_change < highest_24h_change - held_coins[coin_market]['sell_threshold']:
            cur_coin_price = float(coin_info['Last'])

            coin_to_sell = utils.get_second_market_coin(coin_market)
            amount = float(api.get_balance(coin_to_sell)['result']['Available'])

            if amount:
                sell(amount, coin_to_sell, cur_coin_price, coin_market, cur_24h_change)


api = utils.get_api()
held_coins = utils.file_to_json("held_coins.json")

buy_min_percent = 10
buy_max_percent = 100

buy_desired_1h_change = 3

# Also never remove from list until actually sold


def clean_orders():
    orders = api.get_open_orders("")['result']
    for order in orders:
        time_opened = order['Opened']
        time_passed = utils.get_time_passed_minutes(time_opened)

        if time_passed > 10:
            uuid = order['OrderUuid']
            api.cancel(order['OrderUuid'])



# Main Driver
while True:
    #clean_orders()

    # Buy
    total_bitcoin = utils.get_total_bitcoin(api)

    if total_bitcoin > 0:
        find_and_buy(total_bitcoin)

    # Sell
    update_and_or_sell()

    # Clean unsold or unbought orders
    clean_orders()

    time.sleep(10)
