import sys
sys.path.append('../../')

import Trader.Utils as utils
import Trader.Main.Keltner_strat as KS
import Trader.Main.Percent_strat as PS
import Trader.Main.Random_strat as RandS
import Trader.Main.Hodl_strat as HS
import Trader.Main.Reddit_strat as RS
import Trader.Main.Buy_Low_sell_high_strat as LH
import traceback
import time


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

    pending_orders = utils.file_to_json("pending_orders.json")

    for order in orders:
        time_opened = order['Opened']
        time_passed = utils.get_time_passed_minutes(time_opened)

        uuid = order['OrderUuid']
        market = ""

        buying_or_selling = 'Buying' if order['OrderType'] == 'LIMIT_BUY' else 'Selling'

        for pending_market in pending_orders[buying_or_selling]:
            if pending_orders[buying_or_selling][pending_market]['uuid'] == uuid:
                market = pending_market

        if time_passed > time_until_cancel_processing_order_minutes:
            uuid = order['OrderUuid']
            cancel_order = api.cancel(uuid)

            if cancel_order['success']:

                if market in pending_orders[buying_or_selling]:
                    del pending_orders[buying_or_selling][market]

                    utils.json_to_file(pending_orders, "pending_orders.json")
                    utils.print_and_write_to_logfile(
                        "Cancel Order of " + str(order["Quantity"]) + " " + str(order['Exchange']) + " Successful " + utils.get_date_time())
            else:
                utils.print_and_write_to_logfile(
                    "Cancel Order of " + str(order["Quantity"]) + order['Exchange'] + " Unsuccessful: " + cancel_order[
                        'message'] + " " + utils.get_date_time())


def move_to_from_held(pending_market, buying_or_selling):
    """
    Moves a coin from pending_orders.json
    to held_coins
    :param pending_market:
    :param buying_or_selling:
    :return:
    """

    held_coins = utils.file_to_json("held_coins.json")
    pending_orders = utils.file_to_json("pending_orders.json")

    global_return = utils.file_to_json('global_return.json')

    pending_order = pending_orders[buying_or_selling][pending_market]

    if buying_or_selling == 'Buying':
        held_coins[pending_order['market']] = pending_order
        utils.json_to_file(held_coins, 'held_coins.json')
        global_return['Invested'] += pending_orders['Buying'][pending_market]['total_paid']

    elif buying_or_selling == 'Selling':
        del held_coins[pending_market]
        utils.json_to_file(held_coins, "held_coins.json")
        global_return['Gain'] += pending_orders['Selling'][pending_market]['gain']

    utils.json_to_file(global_return, 'global_return.json')
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

    pending_orders = utils.file_to_json("pending_orders.json")

    # Move processed buy orders from pending_orders into held_coins
    processing_orders = [order['OrderUuid'] for order in orders]

    buy_uuids_markets = [(pending_orders['Buying'][market]['uuid'], market) for market in pending_orders['Buying']]

    for buy_uuids_market in buy_uuids_markets:
        buy_uuid = buy_uuids_market[0]
        if buy_uuid not in processing_orders:
            buy_market = buy_uuids_market[1]

            pending_buy_order = pending_orders['Buying'][buy_market]
            amount = str(pending_buy_order['amount'])
            utils.print_and_write_to_logfile(
                "Buy order: " + amount + " of " + buy_market + " Processed Successfully " + "UUID: "
                + buy_uuid + " " + utils.get_date_time())
            move_to_from_held(buy_market, 'Buying')

            # Add price to highest_price_history
            highest_price_list = utils.file_to_json("coin_highest_price_history.json")
            highest_price_list[buy_market] = pending_orders['Buying'][buy_market]['price_bought']
            utils.json_to_file(highest_price_list, 'coin_highest_price_history.json')

    # Move processed sold orders from pending_orders into held_coins
    sell_uuids_markets = [(pending_orders['Selling'][market]['uuid'], market) for market in pending_orders['Selling']]

    for sell_uuids_market in sell_uuids_markets:
        if sell_uuids_market[0] not in processing_orders:
            pending_sell_order = pending_orders['Selling'][sell_uuids_market[1]]
            amount = str(pending_sell_order['amount'])
            utils.print_and_write_to_logfile(
                "Sell order: " + amount + " of " + " " + sell_uuids_market[1] + " Processed Successfully " + "UUID: "
                + sell_uuids_market[0] + " " + utils.get_date_time())
            move_to_from_held(sell_uuids_market[1], 'Selling')


def initialize_random_strat():
    total_slots = 5
    return RandS.RandomStrat(api, total_slots)


def run_random_strat():
    rands.refresh_held_pending()
    rands.update_bittrex_coins()

    if total_bitcoin > satoshi_50k:
        rands.random_buy_strat(total_bitcoin)

    time.sleep(60)

def initialize_hodl_strat():
    # markets_desired_gain = [('BTC-STRAT', 20), ('BTC-SAFEX', 20)]
    markets_desired_gain = []
    total_slots = 5
    return HS.HodlStrat(api, markets_desired_gain, total_slots)


def run_hodl_strat():
    hs.refresh_held_pending()
    hs.update_bittrex_coins()

    if total_bitcoin > satoshi_50k and len(hs.markets_desired_gain) != 0:
        hs.hodl_buy_strat(total_bitcoin)

    hs.hodl_sell_strat()
    time.sleep(60)


def initialize_buy_low_sell_high_strat():
    desired_gain = 20
    desired_low_point = -10

    total_slots = 4
    return LH.BuyLowSellHighStrat(api, desired_gain, desired_low_point, total_slots)



def run_buy_low_sell_high_strat():
    if hl.count_until_reddit_strat == 0:
        run_reddit_strat()
        hl.count_until_reddit_strat = 360
    hl.count_until_reddit_strat -= 1

    hl.refresh_held_pending()
    hl.update_bittrex_coins()

    if total_bitcoin > satoshi_50k:
        hl.low_high_buy_strat(total_bitcoin)

    hl.low_high_sell_strat()
    time.sleep(10)


def initialize_keltner_strat():
    keltner_period = 10
    keltner_multiplier = 1.5
    keltner_slots = 2
    lowest_rank = 50

    ks_instance = KS.KeltnerStrat(api, keltner_period, keltner_multiplier, keltner_slots, lowest_rank)

    # Do keltner math on all bittrex coins once

    ks_instance.add_bittrex_coins_to_keltner_coins(ks_instance.coinmarketcap_coins)

    return ks_instance


def run_keltner_strat():
    ks.refresh_held_pending()

    ks.coinmarketcap_coins = ks.update_coinmarketcap_coins()

    ks.bittrex_coins = ks.update_bittrex_coins(ks.coinmarketcap_coins)

    ks.update_keltner_coins()

    if total_bitcoin > satoshi_50k:
        ks.keltner_buy_strat(total_bitcoin)

    ks.keltner_sell_strat()
    time.sleep(10)


def initialize_reddit_strat():
    reddit_api = utils.get_reddit_api()

    total_slots = 5
    return RS.RedditStrat(api, reddit_api, total_slots)


def run_reddit_strat():
    rs.refresh_held_pending()

    rs.update_reddit_coins()

    rs.update_bittrex_coins()

    rs.store_top_10_data()

    # if total_bitcoin > satoshi_50k:
    #     rs.reddit_buy_strat(total_bitcoin)

    # rs.reddit_sell_strat()


def initialize_percent_strat():
    utils.init_global_return()
    buy_min_percent = 30
    buy_max_percent = 1000
    buy_desired_1h_change = 10
    total_slots = 4
    data_ticks_to_save = 180

    return PS.PercentStrat(api, buy_min_percent, buy_max_percent, buy_desired_1h_change, total_slots, data_ticks_to_save)


def run_percent_strat():
    ps.refresh_held_pending_history()
    ps.update_bittrex_coins()

    ps.historical_coin_data = utils.update_historical_coin_data(ps.historical_coin_data, ps.bittrex_coins, ps.data_ticks_to_save)

    ps.update_coinmarketcap_coins()
    if total_bitcoin > satoshi_50k:
        ps.percent_buy_strat(total_bitcoin)

    ps.percent_sell_strat()
    time.sleep(10)

api = utils.get_api()

time_until_cancel_processing_order_minutes = 5
satoshi_50k = 0.0005

ks = initialize_keltner_strat()
ps = initialize_percent_strat()
hs = initialize_hodl_strat()
rs = initialize_reddit_strat()
hl = initialize_buy_low_sell_high_strat()
rands = initialize_random_strat()


utils.print_and_write_to_logfile("\n** Beginning run at " + utils.get_date_time() + " **\n")


# Main Driver
while True:
    try:

        total_bitcoin = utils.get_total_bitcoin(api)

        # run_keltner_strat()
        # run_percent_strat()
        # run_hodl_strat()
        # run_reddit_strat()
        # run_buy_low_sell_high_strat()
        run_random_strat()

        orders_query = api.get_open_orders("")

        if orders_query['success']:
            orders = orders_query['result']

            clean_orders(orders)
            update_pending_orders(orders)

    except Exception as e:
        utils.print_and_write_to_logfile(traceback.format_exc())
