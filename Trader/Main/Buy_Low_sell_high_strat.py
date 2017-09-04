import Trader.Utils as utils
import sys

sys.path.append('../../')


class BuyLowSellHighStrat:
    satoshi_50k = 0.0005

    def __init__(self, api, desired_gain, desired_low_point, total_slots):
        self.api = api
        self.desired_gain = desired_gain
        self.desired_low_point = desired_low_point
        self.total_slots = total_slots
        self.count_until_reddit_strat = 0

        self.bittrex_coins = utils.get_updated_bittrex_coins()

        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")

    def low_high_buy_strat(self, total_bitcoin):

        top_reddit_coins = utils.file_to_json('reddit_top_coins.json')
        markets_to_ignore = ['BTC-ETH', 'BTC-NEO, BTC-BTC']
        for rank in range(len(top_reddit_coins)):
            market = top_reddit_coins[str(rank)]['market']
            if market not in markets_to_ignore:
                slots_open = self.total_slots - len(self.held_coins) - len(self.pending_orders['Buying']) - len(
                    self.pending_orders['Selling'])
                bitcoin_to_use = float(total_bitcoin / (slots_open + .25))

                coins_pending_buy = [market for market in self.pending_orders['Buying']]
                coins_pending_sell = [market for market in self.pending_orders['Selling']]

                if market not in self.held_coins and market not in coins_pending_buy and market not in \
                        coins_pending_sell:

                    self.update_bittrex_coins()

                    coin_price = float(self.bittrex_coins[market]['Last'])
                    amount = bitcoin_to_use / coin_price

                    if amount > 0:
                        percent_change_24h = utils.get_percent_change_24h(self.bittrex_coins[market])
                        if percent_change_24h <= self.desired_low_point:
                            result = utils.buy(self.api, market, amount, coin_price, percent_change_24h,
                                               self.desired_gain, 0)
                            if not result['success']:
                                utils.print_and_write_to_logfile("Failed to make buy order " + market)

    def low_high_sell_strat(self):
        for market in self.held_coins:
            cur_price = float(self.bittrex_coins[market]['Last'])
            bought_price = self.held_coins[market]['price_bought']
            change = utils.percent_change(bought_price, cur_price)

            desired_gain = self.held_coins[market]['desired_gain']

            if change >= desired_gain:
                coin_to_sell = utils.get_second_market_coin(market)
                balance = self.api.get_balance(coin_to_sell)
                if balance['success']:
                    amount = float(balance['result']['Available'])
                    self.update_bittrex_coins()
                    utils.sell(self.api, amount, market, self.bittrex_coins)
                else:
                    utils.print_and_write_to_logfile("Could not retrieve balance: " + balance['message'])

    def refresh_held_pending(self):
        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")

    def update_bittrex_coins(self):
        self.bittrex_coins = utils.get_updated_bittrex_coins()
