import Trader.utils as utils
import time


def buy(market, amount, coin_price, percent_change_24h):
    """
    Makes a buy order and adds the coin to pending_orders
    :param market:
    :param amount:
    :param coin_price:
    :param percent_change_24h:
    :return:
    """
    total_to_spend = utils.bitcoin_to_USD(coin_price * amount)

    buy_order = api.buy_limit(market, amount, coin_price)

    if buy_order['success']:
        coin_price_usd = utils.bitcoin_to_USD(coin_price)
        time = utils.get_date_time()

        utils.print_and_write_to_logfile("BUYING\n" + market + "\n24h%: " + str(
            percent_change_24h) + "\nUSD: $" + str(coin_price_usd) + "\nBTC: " + str(
            coin_price) + "\nAmount: " + str(amount)
                                         + "\nTotal Paid: $" + str(total_to_spend) + "\nTime: " + time)

        t = {}
        t['market'] = market
        t['highest_24h_change'] = percent_change_24h
        t['original_24h_change'] = percent_change_24h
        t['price_bought'] = coin_price
        t['amount'] = amount
        t['total_paid'] = total_to_spend
        t['sell_threshold'] = 10
        t['uuid'] = buy_order['result']['uuid']

        pending_orders['Buying'][market] = t

        utils.json_to_file(pending_orders, "pending_orders.json")
    else:
        utils.print_and_write_to_logfile(
            "Buy order of " + str(amount) + " " + market + " did not go through: " + buy_order['message'])


def percent_buy_strat(total_bitcoin):
    """
    Searches all coins on bittrex and buys up to the
    variable "total_slots" different coins. Splits the
    amount of bitcoin use on each evenly.

    :param total_bitcoin:
    :return:
    """

    symbol_1h_change_pairs = utils.get_coin_market_cap_1hr_change()

    for coin_key in bittrex_coins:
        slots_open = total_slots - len(held_coins) - len(pending_orders['Buying'])
        bitcoin_to_use = float(total_bitcoin / (slots_open + .25))

        if slots_open <= 0:
            utils.print_and_write_to_logfile("0 slots open")
            break
        if bitcoin_to_use < satoshi_50k:
            utils.print_and_write_to_logfile("Order less than 50k satoshi (~$2). Attempted to use: $" + str(
                utils.bitcoin_to_USD(bitcoin_to_use)) + ", BTC: " + str(bitcoin_to_use))
            break

        percent_change_24h = utils.get_percent_change_24h(bittrex_coins[coin_key])
        if buy_min_percent <= percent_change_24h <= buy_max_percent:
            market = bittrex_coins[coin_key]['MarketName']
            if market.startswith('ETH'):
                break
            if market.startswith('BTC'):

                coin_to_buy = utils.get_second_market_coin(market)
                coin_1h_change = float(symbol_1h_change_pairs[coin_to_buy])

                coins_pending_buy = [market for market in pending_orders['Buying']]
                coins_pending_sell = [market for market in pending_orders['Selling']]

                if market not in held_coins and market not in coins_pending_buy and market not in \
                        coins_pending_sell and coin_1h_change > buy_desired_1h_change:

                    coin_price = float(bittrex_coins[coin_key]['Last'])
                    amount = bitcoin_to_use / coin_price
                    if amount > 0:
                        buy(market, amount, coin_price, percent_change_24h)


def updated_threshold(market, coins):
    """
    Updates the amount from a coin's 24h % peak
    we will allow it to go before selling
    :param market:
    :param coins:
    :return:
    """
    coin = coins[market]
    original_24h_change = coin['original_24h_change']
    h = coin['highest_24h_change']
    cur_threshold = coin['sell_threshold']
    total_change = h - original_24h_change
    return 10


def sell(amount, coin_to_sell, cur_coin_price, coin_market, cur_24h_change):
    """
    Makes a sell order and adds the coin to pending_orders
    :param amount:
    :param coin_to_sell:
    :param cur_coin_price:
    :param coin_market:
    :param cur_24h_change:
    :return:
    """

    sell_order = api.sell_limit(coin_market, amount, cur_coin_price)
    if sell_order['success']:
        selling_for = utils.bitcoin_to_USD(cur_coin_price * amount)
        net_gain_loss = selling_for - float(held_coins[coin_market]['total_paid'])
        cur_coin_price_usd = utils.bitcoin_to_USD(cur_coin_price)
        cur_date_time = utils.get_date_time()

        utils.print_and_write_to_logfile(
            "SELLING\n" + str(coin_to_sell) + str(
                cur_coin_price) + "\nAmount: " + str(amount) +
            "\n24h%: " + "\nUSD: $" + str(cur_coin_price_usd) + "\nBTC: " + str(
                cur_24h_change) + "\nTotal Paid: $" + str(selling_for) + "\nNet Gain/Loss: " + str(
                net_gain_loss) + "\nTime: " + str(time))

        t = {}
        t['coin_to_sell'] = coin_to_sell
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

        pending_orders['Selling'][coin_market] = t
        utils.json_to_file(pending_orders, "pending_orders.json")
    else:
        utils.print_and_write_to_logfile("Sell order did not go through: " + sell_order['message'])


def percent_sell_strat():
    """
    If a coin drops more than its variable "sell threshold"
    from its highest 24 hour % change, it is sold

    Checks the coins current 24 hour % change and
    updates it if it is greater than it's current highest

    :return:
    """

    held_markets = [market for market in held_coins]
    for coin_market in held_markets:
        coin_info = bittrex_coins[coin_market]
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

            balance = api.get_balance(coin_to_sell)

            if balance['success']:
                amount = float(balance['result']['Available'])
                sell(amount, coin_to_sell, cur_coin_price, coin_market, cur_24h_change)
            else:
                utils.print_and_write_to_logfile("Could not retrieve balance: " + balance['message'])


def clean_orders(orders):
    """
    Finds any order that has been attempting to buy
    or sell for longer than the variable
    time_until_cancel_processing_order_minutes
    and attempt to cancel them on bittrex, and
    also deletes them from pending_orders.json

    :param orders:
    :return void:
    """

    for order in orders:
        time_opened = order['Opened']
        time_passed = utils.get_time_passed_minutes(time_opened)

        if time_passed > time_until_cancel_processing_order_minutes:
            uuid = order['OrderUuid']
            cancel_order = api.cancel(order['OrderUuid'])
            if cancel_order['success']:
                buying_or_selling = 'Buying' if order['OrderType'] == 'Limit_Buy' else 'Selling'

                pending_uuids_markets = [(pending_orders[buying_or_selling][market]['uuid'], market) for market in
                                      pending_orders[buying_or_selling]]

                for uuid_market in pending_uuids_markets:
                    if uuid_market[0] == uuid:
                        del pending_orders[buying_or_selling][uuid_market][1]
                        break

                utils.json_to_file(pending_orders, "pending_orders.json")
                utils.print_and_write_to_logfile(
                    "Cancel Order of " + order["Quantity"] + order['Exchange'] + " Successful")
            else:
                utils.print_and_write_to_logfile(
                    "Cancel Order of " + order["Quantity"] + order['Exchange'] + " Unsuccessful: " + cancel_order[
                        'message'])


def move_to_held(pending_market, buying_or_selling):
    """
    Moves a coin from pending_orders.json
    to held_coins

    :param pending_uuid:
    :param buying_or_selling:
    :return:
    """

    pending_order = pending_orders[buying_or_selling][pending_market]

    if buying_or_selling == 'Buying':
        held_coins[pending_order['market']] = pending_order
        utils.json_to_file(held_coins, "held_coins.json")

    elif buying_or_selling == 'Selling':
        del held_coins[pending_order['market']]
        utils.json_to_file(held_coins, "held_coins.json")

    del pending_orders[buying_or_selling][pending_market]
    utils.json_to_file(pending_orders, "pending_orders.json")


def update_pending_orders(orders):
    """
    Checks bitttrex's open orders and if a coin that's in
    pending_orders is no longer in bittrex's pending orders
    it has gone through, so we add it to our held coins.
    :param orders:
    :return:
    """

    # Move processed buy orders from pending_orders into held_coins
    processing_orders = [order['OrderUuid'] for order in orders]

    buy_uuids_markets = [(pending_orders['Buying'][market]['uuid'], market) for market in pending_orders['Buying']]

    for buy_uuids_market in buy_uuids_markets:
        if buy_uuids_market[0] not in processing_orders:
            pending_buy_order = pending_orders['Buying'][buy_uuids_market[1]]
            amount = str(pending_buy_order['amount'])
            utils.print_and_write_to_logfile(
                "Buy order: " + amount + " of " + " " + buy_uuids_market[1] + " Processed Successfully " + "UUID: "
                + buy_uuids_market[0])
            move_to_held(buy_uuids_market[1], 'Buying')

    sell_uuids_markets = [(pending_orders['Selling'][market]['uuid'], market) for market in pending_orders['Selling']]

    # Move processed sold orders from pending_orders into held_coins
    for sell_uuids_market in sell_uuids_markets:
        if sell_uuids_market[0] not in processing_orders:
            pending_sell_order = pending_orders['Selling'][sell_uuids_market[1]]
            amount = str(pending_sell_order['amount'])
            utils.print_and_write_to_logfile(
                "Sell order: " + amount + " of " + " " + sell_uuids_market[1] + " Processed Successfully " + "UUID: "
                + sell_uuids_market[0])
            move_to_held(sell_uuids_market[1], 'Selling')


def update_bittrex_coins():
    bittrex_data = utils.query_url("https://bittrex.com/api/v1.1/public/getmarketsummaries")['result']

    for coin in bittrex_data:
        key = coin['MarketName']
        bittrex_coins[key] = coin


def add_to_keltner_coins(symbol):
    trade = 'BTC'
    market = '{0}-{1}'.format(trade, symbol)

    coin_data = bittrex_coins[market]

    t = {}
    t['market'] = market
    t['price_data'] = []
    t['tr_data'] = []
    t['atr_data'] = []
    t['ema_data'] = []
    t['upper_band_data'] = []
    t['middle_band_data'] = []
    t['lower_band_data'] = []

    keltner_coins[market] = t
    utils.json_to_file(keltner_coins, "keltner_coins.json")


def update_keltner_coins():
    for market in keltner_coins:
        update_atr(market)
        update_ema(market)
        update_bands(market)
    utils.json_to_file(keltner_coins, "keltner_coins.json")


def update_atr(market):
    if market in keltner_coins:
        bittrex_coin = bittrex_coins[market]

        keltner_coin = keltner_coins[market]

        price_data = keltner_coin['price_data']

        tr_data = keltner_coin['tr_data']

        cur_price = bittrex_coin['Last']

        if len(price_data) == keltner_period:

            period_low = min(price_data)
            period_high = max(price_data)


            cur_tr = max([period_high - period_low, abs(period_high - cur_price), abs(period_low - cur_price)])

            if len(tr_data) == keltner_period:
                atr_data = keltner_coin['atr_data']
                if len(atr_data) == 0:
                    atr_data.append(sum(tr_data) / keltner_period)
                else:
                    last_atr = atr_data[-1]

                    cur_atr = (last_atr * (keltner_period - 1) + cur_tr) / keltner_period

                    if len(atr_data) == keltner_period:
                        atr_data.pop(0)
                    atr_data.append(cur_atr)

                keltner_coin['tr_data'].pop(0)

            keltner_coin['tr_data'].append(cur_tr)

            keltner_coin['price_data'].pop(0)

        keltner_coin['price_data'].append(cur_price)


def update_ema(market):
    if market in keltner_coins:
        keltner_coin = keltner_coins[market]

        price_data = keltner_coin['price_data']

        if len(price_data) < keltner_period:
            return

        cur_price = price_data[-1]
        ema_data = keltner_coin["ema_data"]

        cur_ema = 0
        if len(ema_data) == 0:
            cur_ema = sum(price_data)/keltner_period

        else:
            prev_ema = ema_data[-1]
            multiplier = 2 / (keltner_period + 1) + prev_ema
            cur_ema = (cur_price - prev_ema) * multiplier + prev_ema

        if len(ema_data) == keltner_period:
            keltner_coin['ema_data'].pop(0)

        keltner_coin['ema_data'].append(cur_ema)


def update_bands(market):
    if market in keltner_coins and len(keltner_coins[market]['atr_data']) == keltner_period:
        keltner_coin = keltner_coins[market]
        cur_ema = keltner_coin['ema_data'][-1]
        cur_atr = keltner_coin['atr_data'][-1]

        upper_band = cur_ema + cur_atr * keltner_multiplier
        middle_band = cur_ema
        lower_band = cur_ema - cur_atr * keltner_multiplier

        keltner_coins[market]['upper_band_data'].append(upper_band)
        keltner_coins[market]['middle_band_data'].append(middle_band)
        keltner_coins[market]['lower_band_data'].append(lower_band)
        if len(keltner_coins[market]['upper_band_data']) > keltner_period:
            keltner_coins[market]['upper_band_data'].pop(0)
            keltner_coins[market]['middle_band_data']
            keltner_coins[market]['lower_band_data']


def get_upper_band(market):
    if market in keltner_coins and len(keltner_coins[market]['atr_data']) == keltner_period:
        keltner_coin = keltner_coins[market]
        if len(keltner_coin['upper_band']) > 0:
            return keltner_coin['upper_band'][-1]
    return -1


def get_middle_band(market):
    if market in keltner_coins and len(keltner_coins[market]['atr_data']) == keltner_period:
        keltner_coin = keltner_coins[market]
        if len(keltner_coin['middle_band']) > 0:
            return keltner_coin['middle_band'][-1]
    return -1


def get_lower_band(market):
    if market in keltner_coins and len(keltner_coins[market]['atr_data']) == keltner_period:
        keltner_coin = keltner_coins[market]
        if len(keltner_coin['lower_band']) > 0:
            return keltner_coin['lower_band'][-1]
    return -1


def keltner_buy_strat(total_bitcoin):
    # total_to_spend = utils.bitcoin_to_USD(coin_price * amount)
    return


def keltner_sell_strat():
    return


def find_keltner_coins():
    return


def reset_keltner_coins():
    keltner_coins = utils.file_to_json("keltner_coins.json")
    for coin in keltner_coins:
        keltner_coins[coin]['price_data'] = []
        keltner_coins[coin]['tr_data'] = []
        keltner_coins[coin]['atr_data'] = []
        keltner_coins[coin]['ema_data'] = []
        keltner_coins[coin]['upper_band_data'] = []
        keltner_coins[coin]['middle_band_data'] = []
        keltner_coins[coin]['lower_band_data'] = []
    utils.json_to_file(keltner_coins, "keltner_coins.json")
    return keltner_coins


api = utils.get_api()

held_coins = utils.file_to_json("held_coins.json")
pending_orders = utils.file_to_json("pending_orders.json")

buy_min_percent = 20
buy_max_percent = 30
buy_desired_1h_change = 15
total_slots = 4
time_until_cancel_processing_order_minutes = 10
satoshi_50k = 0.0005
keltner_period = 20
keltner_multiplier = 2

bittrex_coins = {}
keltner_coins = reset_keltner_coins()

utils.print_and_write_to_logfile("\n**Beginning run at " + utils.get_date_time() + "**\n")


# add_to_keltner_coins("DGB")

# Main Driver
while True:
    update_bittrex_coins()

    #update_keltner_coins()

    # Buy
    total_bitcoin = utils.get_total_bitcoin(api)

    if total_bitcoin > satoshi_50k:
        percent_buy_strat(total_bitcoin,)
        #keltner_buy_strat(total_bitcoin)

    # Sell
    percent_sell_strat()
    # keltner_sell_strat()

    orders = api.get_open_orders("")['result']

    clean_orders(orders)
    update_pending_orders(orders)

    time.sleep(10)