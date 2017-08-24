import Trader.Utils as utils
import sys
sys.path.append('../../')

class KeltnerStrat:
    def __init__(self, api, keltner_period, keltner_multiplier, keltner_slots, keltner_prev_ticks):
        self.api = api
        self.keltner_period = keltner_period
        self.keltner_multiplier = keltner_multiplier
        self.keltner_slots = keltner_slots
        self.keltner_prev_ticks = keltner_prev_ticks

        self.keltner_coins = utils.file_to_json("keltner_coins.json")
        self.bittrex_coins = utils.get_updated_bittrex_coins()

        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")

        self.reset_keltner_coins()

    def refresh_held_pending(self):
        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")

    def update_keltner_coins(self):
        for market in self.keltner_coins:
            self.update_atr(market)
            self.update_ema(market)
            self.update_bands(market)
        utils.json_to_file(self.keltner_coins, "keltner_coins.json")

    def update_atr(self, market):
        if market in self.keltner_coins:
            bittrex_coin = self.bittrex_coins[market]

            keltner_coin = self.keltner_coins[market]

            price_data = keltner_coin['price_data']

            tr_data = keltner_coin['tr_data']

            cur_price = bittrex_coin['Last']

            if len(price_data) == self.keltner_period:

                period_low = min(price_data)
                period_high = max(price_data)

                cur_tr = max([period_high - period_low, abs(period_high - cur_price), abs(period_low - cur_price)])

                if len(tr_data) == self.keltner_period:
                    atr_data = keltner_coin['atr_data']
                    if len(atr_data) == 0:
                        atr_data.append(sum(tr_data) / self.keltner_period)
                    else:
                        last_atr = atr_data[-1]

                        cur_atr = (last_atr * (self.keltner_period - 1) + cur_tr) / self.keltner_period

                        if len(atr_data) == self.keltner_period:
                            atr_data.pop(0)
                        atr_data.append(cur_atr)

                    keltner_coin['tr_data'].pop(0)

                keltner_coin['tr_data'].append(cur_tr)

                keltner_coin['price_data'].pop(0)

            keltner_coin['price_data'].append(cur_price)

    def update_ema(self, market):
        if market in self.keltner_coins:
            keltner_coin = self.keltner_coins[market]

            price_data = keltner_coin['price_data']

            if len(price_data) == self.keltner_period:

                cur_price = price_data[-1]
                ema_data = keltner_coin["ema_data"]

                if len(ema_data) == 0:
                    cur_ema = sum(price_data) / self.keltner_period

                else:
                    prev_ema = ema_data[-1]
                    multiplier = 2 / (self.keltner_period + 1) + prev_ema
                    cur_ema = (cur_price - prev_ema) * multiplier + prev_ema

                if len(ema_data) == self.keltner_period:
                    keltner_coin['ema_data'].pop(0)

                keltner_coin['ema_data'].append(cur_ema)

    def update_bands(self, market):
        if market in self.keltner_coins and len(self.keltner_coins[market]['atr_data']) == self.keltner_period:
            keltner_coin = self.keltner_coins[market]
            cur_ema = keltner_coin['ema_data'][-1]
            cur_atr = keltner_coin['atr_data'][-1]

            upper_band = cur_ema + cur_atr * self.keltner_multiplier
            middle_band = cur_ema
            lower_band = cur_ema - cur_atr * self.keltner_multiplier

            self.keltner_coins[market]['upper_band_data'].append(upper_band)
            self.keltner_coins[market]['middle_band_data'].append(middle_band)
            self.keltner_coins[market]['lower_band_data'].append(lower_band)
            if len(self.keltner_coins[market]['upper_band_data']) > self.keltner_period:
                self.keltner_coins[market]['upper_band_data'].pop(0)
                self.keltner_coins[market]['middle_band_data'].pop(0)
                self.keltner_coins[market]['lower_band_data'].pop(0)

    def get_upper_band(self, market):
        if market in self.keltner_coins and len(self.keltner_coins[market]['atr_data']) == self.keltner_period:
            keltner_coin = self.keltner_coins[market]
            if len(keltner_coin['upper_band']) > 0:
                return keltner_coin['upper_band'][-1]
        return -1

    def get_middle_band(self, market):
        if market in self.keltner_coins and len(self.keltner_coins[market]['atr_data']) == self.keltner_period:
            keltner_coin = self.keltner_coins[market]
            if len(keltner_coin['middle_band']) > 0:
                return keltner_coin['middle_band'][-1]
        return -1

    def get_lower_band(self, market):
        if market in self.keltner_coins and len(self.keltner_coins[market]['atr_data']) == self.keltner_period:
            keltner_coin = self.keltner_coins[market]
            if len(keltner_coin['lower_band']) > 0:
                return keltner_coin['lower_band'][-1]
        return -1

    def upward_cross(self, market, upper_middle_or_lower_data):
        x = self.keltner_prev_ticks * -1 - 1
        last_x_prices = self.keltner_coins[market]['price_data'][x:-1]
        last_x_bands = upper_middle_or_lower_data[x:-1]
        for i in range(len(last_x_prices)):
            if last_x_prices[i] > last_x_bands[i]:
                return False
        cur_price = self.keltner_coins[market]['price_data'][-1]
        cur_band = upper_middle_or_lower_data[-1]
        if cur_price > cur_band:
            return True
        return False

    def downward_cross(self, market, upper_middle_or_lower_data):
        x = self.keltner_prev_ticks * -1 - 1
        last_x_prices = self.keltner_coins[market]['price_data'][x:-1]
        last_x_bands = upper_middle_or_lower_data[x:-1]
        for i in range(len(last_x_prices)):
            if last_x_prices[i] < last_x_bands[i]:
                return False
        cur_price = self.keltner_coins[market]['price_data'][-1]
        cur_band = upper_middle_or_lower_data[-1]
        if cur_price < cur_band:
            return True
        return False

    def reset_keltner_coins(self):
        self.keltner_coins = utils.file_to_json("keltner_coins.json")
        for coin in self.keltner_coins:
            self.keltner_coins[coin]['price_data'] = []
            self.keltner_coins[coin]['tr_data'] = []
            self.keltner_coins[coin]['atr_data'] = []
            self.keltner_coins[coin]['ema_data'] = []
            self.keltner_coins[coin]['upper_band_data'] = []
            self.keltner_coins[coin]['middle_band_data'] = []
            self.keltner_coins[coin]['lower_band_data'] = []
        utils.json_to_file(self.keltner_coins, "keltner_coins.json")

    def keltner_buy_strat(self, total_bitcoin):
        keltner_slots_open = self.keltner_slots - len(self.held_coins) - len(self.pending_orders['Buying']) - len(
            self.pending_orders['Selling'])

        for coin in self.keltner_coins:
            market = self.bittrex_coins[coin]['MarketName']
            lower_band_data = self.keltner_coins[market]['lower_band_data']
            if len(lower_band_data) == self.keltner_period:
                coins_pending_buy = [market for market in self.pending_orders['Buying']]
                coins_pending_sell = [market for market in self.pending_orders['Selling']]

                if market not in self.held_coins and market not in coins_pending_buy and market not in coins_pending_sell:

                    price_data = self.keltner_coins[market]['price_data']
                    cur_price = float(price_data[-1])

                    if cur_price > self.keltner_coins[market]['lower_band_data'][-1] and cur_price > max(price_data):
                        bitcoin_to_use = float(total_bitcoin / (keltner_slots_open + .25))
                        amount = bitcoin_to_use / cur_price
                        percent_change_24h = utils.get_percent_change_24h(coin)
                        utils.buy(self.api, market, amount, cur_price, percent_change_24h, 0)

    def keltner_sell_strat(self):

        for coin in self.keltner_coins:
            market = self.bittrex_coins[coin]['MarketName']
            lower_band_data = self.keltner_coins[market]['lower_band_data']

            if len(lower_band_data) == self.keltner_period:
                market = self.bittrex_coins[coin]['MarketName']
                coins_pending_buy = [market for market in self.pending_orders['Buying']]
                coins_pending_sell = [market for market in self.pending_orders['Selling']]

                if market not in coins_pending_buy and market not in coins_pending_sell and market in self.held_coins:
                    lower_band_data = self.keltner_coins[market]['upper_bound_data']
                    #if self.downward_cross(market, lower_band_data) or self.downward_cross(market, lower_band_data):
                    # Find the max and the min of the price in the last 20 ticks
                    # Find the difference between the min and max
                    # Deviation = difference/cur_price
                    # Sell if price goes down by more than than 2*deviation in terms of percent

                    price_data = self.keltner_coins[market]['price_data']

                    # This is where we need to add stuff
                    cur_price = price_data[-1]
                    max_price = max(price_data)
                    min_price = min(price_data)
                    diff = max_price - min_price
                    deviation = diff/cur_price
                    if cur_price < 2*deviation:
                        coin_to_sell = utils.get_second_market_coin(market)
                        balance = self.api.get_balance(coin_to_sell)
                        if balance['success']:
                            amount = float(balance['result']['Available'])
                            utils.sell(self.api, amount, market, self.bittrex_coins)
                        else:
                            utils.print_and_write_to_logfile("Could not retrieve balance: " + balance['message'])

    def update_bittrex_coins(self):
        self.bittrex_coins = utils.get_updated_bittrex_coins()

    def add_to_keltner_coins(self, market):

        t = {}
        t['market'] = market
        t['price_data'] = []
        t['tr_data'] = []
        t['atr_data'] = []
        t['ema_data'] = []
        t['upper_band_data'] = []
        t['middle_band_data'] = []
        t['lower_band_data'] = []

        self.keltner_coins[market] = t
        utils.json_to_file(self.keltner_coins, "keltner_coins.json")

    def add_bittrex_coins_to_keltner_coins(self):
        self.keltner_coins = {}
        self.update_bittrex_coins()
        for market in self.bittrex_coins:
            if market.startswith('BTC'):
                coin_data = self.bittrex_coins[market]

                t = {}
                t['market'] = market
                t['price_data'] = []
                t['tr_data'] = []
                t['atr_data'] = []
                t['ema_data'] = []
                t['upper_band_data'] = []
                t['middle_band_data'] = []
                t['lower_band_data'] = []

                self.keltner_coins[market] = t

        utils.json_to_file(self.keltner_coins, "keltner_coins.json")
