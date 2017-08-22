import Trader.utils as utils
import Trader.Main.keltner_strat as KS
import Trader.Main.percent_strat as PS
import Trader.Main.hodl_strat as HS
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

    held_coins = utils.file_to_json("held_coins.json")
    pending_orders = utils.file_to_json("pending_orders.json")

    pending_order = pending_orders[buying_or_selling][pending_market]

    if buying_or_selling == 'Buying':
        held_coins[pending_order['market']] = pending_order
        utils.json_to_file(held_coins, "held_coins.json")

    elif buying_or_selling == 'Selling':
        del held_coins[pending_market]
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

    held_coins = utils.file_to_json("held_coins.json")
    pending_orders = utils.file_to_json("pending_orders.json")

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


def initialize_hodl_strat():
    # markets_desired_gain = [('BTC-LSK', 10)]
    markets_desired_gain = []
    total_slots = 5
    return HS.HodlStrat(api, markets_desired_gain, total_slots)


def run_hodl_strat():
    hs.refresh_held_pending()

    if total_bitcoin > satoshi_50k and len(hs.markets_desired_gain) != 0:
        hs.hodl_buy_strat(total_bitcoin)

    hs.update_bittrex_coins()
    hs.hodl_sell_strat()


def initialize_percent_strat():
    buy_min_percent = 20
    buy_max_percent = 30
    buy_desired_1h_change = 15
    total_slots = 4
    return PS.PercentStrat(api, buy_min_percent, buy_max_percent, buy_desired_1h_change, total_slots)


def run_percent_strat():
    ps.refresh_held_pending()
    if total_bitcoin > satoshi_50k:
        ps.percent_buy_strat(total_bitcoin,)

    ps.percent_sell_strat()

    ps.update_bittrex_coins()


def initialize_keltner_strat():
    keltner_period = 20
    keltner_multiplier = 2
    keltner_slots = 2
    keltner_prev_ticks = 3

    # Uncomment to do keltner math on all bittrex coins once
    # ks.add_bittrex_coins_to_keltner_coins()

    return KS.KeltnerStrat(api, keltner_period, keltner_multiplier, keltner_slots, keltner_prev_ticks)


def run_keltner_strat():
    ks.refresh_held_pending()

    ks.update_keltner_coins()

    ks.update_bittrex_coins()

    if total_bitcoin > satoshi_50k:
        ks.keltner_buy_strat(total_bitcoin)

    ks.keltner_sell_strat()


api = utils.get_api()

time_until_cancel_processing_order_minutes = 10
satoshi_50k = 0.0005

ks = initialize_keltner_strat()
ps = initialize_percent_strat()
hs = initialize_hodl_strat()

utils.print_and_write_to_logfile("\n**Beginning run at " + utils.get_date_time() + "**\n")

# Main Driver
while True:
    total_bitcoin = utils.get_total_bitcoin(api)

    run_keltner_strat()
    # run_percent_strat()
    # run_hodl_strat()

    orders = api.get_open_orders("")['result']
    clean_orders(orders)
    update_pending_orders(orders)

    time.sleep(10)
