import Trader.Utils as utils
import sys
sys.path.append('../../')


class RandomStrat:
    satoshi_50k = 0.0005

    def __init__(self, api, total_slots):
        self.api = api
        self.total_slots = total_slots

        self.bittrex_coins = utils.get_updated_bittrex_coins()

        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")

    def random_buy_strat(self, total_bitcoin):

        slots_open = self.total_slots - len(self.held_coins) - len(self.pending_orders['Buying']) - len(
            self.pending_orders['Selling'])
        bitcoin_to_use = float(total_bitcoin / (slots_open + .25))

        for market_gain_pair in self.markets_desired_gain:
            market = market_gain_pair[0]
            desired_gain = market_gain_pair[1]

            coins_pending_buy = [market for market in self.pending_orders['Buying']]
            coins_pending_sell = [market for market in self.pending_orders['Selling']]

            if market not in self.held_coins and market not in coins_pending_buy and market not in \
                    coins_pending_sell:

                coin_price = float(self.bittrex_coins[market]['Last'])
                amount = bitcoin_to_use / coin_price

                if amount > 0:


                    percent_change_24h = utils.get_percent_change_24h(self.bittrex_coins[market])
                    result = utils.buy(self.api, market, amount, coin_price, percent_change_24h, desired_gain)

    def refresh_held_pending(self):
        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")

    def update_bittrex_coins(self):
        self.bittrex_coins = utils.get_updated_bittrex_coins()