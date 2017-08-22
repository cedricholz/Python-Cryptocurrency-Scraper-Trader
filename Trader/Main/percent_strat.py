import Trader.utils as utils


class PercentStrat:
    satoshi_50k = 0.0005

    def __init__(self, api, buy_min_percent, buy_max_percent, buy_desired_1h_change, total_slots):
        self.api = api
        self.buy_min_percent = buy_min_percent
        self.buy_max_percent = buy_max_percent
        self.buy_desired_1h_change = buy_desired_1h_change
        self.total_slots = total_slots

        self.bittrex_coins = utils.get_updated_bittrex_coins()

        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")

    def percent_buy_strat(self, total_bitcoin):
        """
        Searches all coins on bittrex and buys up to the
        variable "total_slots" different coins. Splits the
        amount of bitcoin use on each evenly.

        :param total_bitcoin:
        :return:
        """

        symbol_1h_change_pairs = utils.get_coin_market_cap_1hr_change()

        for coin_key in self.bittrex_coins:
            slots_open = self.total_slots - len(self.held_coins) - len(self.pending_orders['Buying']) - len(
                self.pending_orders['Selling'])
            bitcoin_to_use = float(total_bitcoin / (slots_open + .25))

            if slots_open <= 0:
                utils.print_and_write_to_logfile("0 slots open")
                break
            if bitcoin_to_use < self.satoshi_50k:
                utils.print_and_write_to_logfile("Order less than 50k satoshi (~$2). Attempted to use: $" + str(
                    utils.bitcoin_to_USD(bitcoin_to_use)) + ", BTC: " + str(bitcoin_to_use))
                break

            percent_change_24h = utils.get_percent_change_24h(self.bittrex_coins[coin_key])
            if self.buy_min_percent <= percent_change_24h <= self.buy_max_percent:
                market = self.bittrex_coins[coin_key]['MarketName']
                if market.startswith('ETH'):
                    break
                if market.startswith('BTC'):

                    coin_to_buy = utils.get_second_market_coin(market)
                    coin_1h_change = float(symbol_1h_change_pairs[coin_to_buy])

                    coins_pending_buy = [market for market in self.pending_orders['Buying']]
                    coins_pending_sell = [market for market in self.pending_orders['Selling']]

                    if market not in self.held_coins and market not in coins_pending_buy and market not in \
                            coins_pending_sell and coin_1h_change > self.buy_desired_1h_change:

                        coin_price = float(self.bittrex_coins[coin_key]['Last'])
                        amount = bitcoin_to_use / coin_price
                        if amount > 0:
                            utils.buy(self.api, market, amount, coin_price, percent_change_24h, 0)

    def percent_sell_strat(self):
        """
        If a coin drops more than its variable "sell threshold"
        from its highest 24 hour % change, it is sold

        Checks the coins current 24 hour % change and
        updates it if it is greater than it's current highest

        :return:
        """

        held_markets = [market for market in self.held_coins]
        for coin_market in held_markets:
            coin_info = self.bittrex_coins[coin_market]
            cur_24h_change = utils.get_percent_change_24h(coin_info)
            highest_24h_change = self.held_coins[coin_market]['highest_24h_change']

            if cur_24h_change > highest_24h_change:
                self.held_coins[coin_market]['highest_24h_change'] = cur_24h_change
                highest_24h_change = cur_24h_change
                utils.json_to_file(self.held_coins, "held_coins.json")

                self.held_coins[coin_market]['sell_threshold'] = self.updated_threshold(coin_market, self.held_coins)
            utils.json_to_file(self.held_coins, "held_coins.json")

            if cur_24h_change < highest_24h_change - self.held_coins[coin_market]['sell_threshold']:
                cur_coin_price = float(coin_info['Last'])

                coin_to_sell = utils.get_second_market_coin(coin_market)

                balance = self.api.get_balance(coin_to_sell)

                if balance['success']:
                    amount = float(balance['result']['Available'])
                    if amount > 0:
                        utils.sell(self.api, amount, coin_to_sell, cur_coin_price, coin_market, cur_24h_change, 0)
                else:
                    utils.print_and_write_to_logfile("Could not retrieve balance: " + balance['message'])

    def updated_threshold(self, market, coins):
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

    def refresh_held_pending(self):
        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")
