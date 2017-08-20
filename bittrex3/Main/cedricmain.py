import bittrex3.utils as utils
import time


def buy(market, amount, coin_price, slots_open, percent_change_24h):
    # buy_order = api.buy_limit(market, amount, coin_price)
    buy_order = {}
    buy_order['success'] = True
    if buy_order['success']:
        total_paid = utils.bitcoin_to_USD(coin_price * amount)
        utils.print_and_write_to_logfile("Bought " + str(amount) + " of " + str(market) + " at " + str(
            coin_price) + ", Total Paid: $" + str(total_paid))
        slots_open -= 1
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


def find_and_buy(slots_open):
    total_bitcoin = float(api.get_balance('BTC')['result']['Available'])

    bittrex_coins = utils.query_url("https://bittrex.com/api/v1.1/public/getmarketsummaries")['result']

    bitcoin_to_use = float(total_bitcoin / (slots_open + .25))
    symbol_1h_change_pairs = utils.get_coin_market_cap_1hr_change()

    for coin in bittrex_coins:
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
                    if market not in held_coins and coin_1h_change > 5:
                        coin_price = float(coin_summary['result']['Last'])
                        amount = bitcoin_to_use / coin_price
                        if amount > 0:
                            buy(market, amount, coin_price, slots_open, percent_change_24h)
                else:
                    utils.print_and_write_to_logfile("Could not obtain coin summary :" + coin_summary['message'])


def sell(amount, coin_to_sell, cur_coin_price, slots_open, coin_market):
    # sell_order = api.sell_limit(market, amount, cur_coin_price)
    sell_order = {}
    sell_order['success'] = True
    if sell_order['success']:
        sold_for = utils.bitcoin_to_USD(cur_coin_price * amount)
        net_gain_loss = sold_for - float(held_coins[coin_market]['total_paid'])

        utils.print_and_write_to_logfile("Sold " + str(amount) + " of " + str(coin_to_sell) + " at " + str(cur_coin_price) + " for $" +
              str(sold_for) + " net gain/net loss: $" + str(net_gain_loss))

        slots_open += 1
        del held_coins[coin_market]
        utils.json_to_file(held_coins, "held_coins.json")
    else:
        utils.print_and_write_to_logfile("Sell order did not go through: " + sell_order['message'])


# def update_threshold(market, coins):
#     coin = coins[market]
#     original_24h_change = coin['original_24h_change']
#     highest_24h_change = coin['highest_24h_change']
#     cur_threshold = coin['sell_threshold']
#     total_change = highest_24h_change - original_24h_change


def update_and_or_sell(slots_open):
    held_markets = [market for market in held_coins]
    for coin_market in held_markets:
        coin_info = utils.query_url("https://bittrex.com/api/v1.1/public/getmarketsummary?market=" + coin_market)['result'][0]

        cur_24h_change = utils.get_percent_change_24h(coin_info)
        highest_24h_change = held_coins[coin_market]['highest_24h_change']

        if cur_24h_change > highest_24h_change:
            held_coins[coin_market]['highest_24h_change'] = cur_24h_change
            highest_24h_change = cur_24h_change
            utils.json_to_file(held_coins, "held_coins.json")

        #update_threshold(coin_market, held_coins)

        if cur_24h_change < highest_24h_change - held_coins[coin_market]['sell_threshold']:
            cur_coin_price = coin_info['Last']

            coin_to_sell = utils.get_second_market_coin(coin_market)
            amount = api.get_balance(coin_to_sell)['result']['Available']

            if amount:
                sell(amount, coin_to_sell, cur_coin_price, slots_open, coin_market)


api = utils.get_api()
held_coins = utils.file_to_json("held_coins.json")
slots_open = 5 - len(held_coins)

buy_min_percent = 30
buy_max_percent = 40


# Main Driver
while True:



    # Buy
    find_and_buy(slots_open)

    # Sell
    update_and_or_sell(slots_open)

    time.sleep(10)