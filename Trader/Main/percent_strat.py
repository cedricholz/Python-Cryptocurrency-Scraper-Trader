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
        self.refresh_held_pending_history()

        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")
        self.history_coins = utils.file_to_json("coin_highest_price_history.json")

    def percent_buy_strat(self, total_bitcoin):
        """
        Searches all coins on bittrex and buys up to the
        variable "total_slots" different coins. Splits the
        amount of bitcoin use on each evenly.

        :param total_bitcoin:
        :return:
        """

        symbol_1h_change_pairs = utils.get_coin_market_cap_1hr_change()

        # update highest price recorded while held
        for coin in self.history_coins:
            if coin in self.held_coins:
                coin_price = float(self.bittrex_coins[coin]['Last'])
                highest_recorded_price = float(self.history_coins[coin]['highest_price_recorded'])
                if coin_price > highest_recorded_price:
                    self.history_coins[coin]['highest_price_recorded'] = coin_price
                    utils.json_to_file(self.history_coins,"coin_highest_price_history.json" )
        for hist_coin in self.history_coins:
            coin_price = float(self.bittrex_coins[hist_coin]['Last'])
            if float(self.history_coins[hist_coin]['highest_price_recorded'])*1.1 < coin_price:
                if hist_coin not in self.held_coins:
                    slots_open = self.total_slots - len(self.held_coins) - len(self.pending_orders['Buying']) - len(
                        self.pending_orders['Selling'])
                    bitcoin_to_use = float(2*total_bitcoin / (slots_open + .25))
                    if slots_open <= 0:
                        utils.print_and_write_to_logfile("0 slots open")
                        break
                    if bitcoin_to_use < self.satoshi_50k:
                        utils.print_and_write_to_logfile("Order less than 50k satoshi (~$2). Attempted to use: $" + str(
                            utils.bitcoin_to_USD(bitcoin_to_use)) + ", BTC: " + str(bitcoin_to_use))
                        break

                    coins_pending_buy = [market for market in self.pending_orders['Buying']]
                    coins_pending_sell = [market for market in self.pending_orders['Selling']]

                    if hist_coin not in coins_pending_buy and hist_coin not in coins_pending_sell:
                        coin_price = float(self.bittrex_coins[hist_coin]['Last'])
                        amount = bitcoin_to_use / coin_price
                        if amount > 0:
                            coin_to_buy = utils.get_second_market_coin(hist_coin)
                            coin_1h_change = float(symbol_1h_change_pairs[coin_to_buy])
                            percent_change_24h = utils.get_percent_change_24h(self.bittrex_coins[hist_coin])
                            utils.buy(self.api, hist_coin, amount, coin_price, percent_change_24h, 0, coin_1h_change)


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
                rank = utils.get_rank()
                coin_rank = rank[utils.get_second_market_coin(coin_key)]
                if float(coin_rank) > 50 and coin_key not in self.history_coins:
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
                                utils.buy(self.api, market, amount, coin_price, percent_change_24h, 0, coin_1h_change)

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

            if cur_24h_change < highest_24h_change - 10:
                cur_coin_price = float(coin_info['Last'])

                coin_to_sell = utils.get_second_market_coin(coin_market)

                balance = self.api.get_balance(coin_to_sell)

                if balance['success']:
                    amount = float(balance['result']['Available'])
                    if amount > 0:
                        utils.sell(self.api, amount, coin_market, self.bittrex_coins)
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
        return 5

    def refresh_held_pending_history(self):
        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")
        self.history_coins = utils.file_to_json("coin_highest_price_history.json")

    def update_bittrex_coins(self):
        self.bittrex_coins = utils.get_updated_bittrex_coins()