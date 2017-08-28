import sys
sys.path.append('../../')
import Trader.Utils as utils
import re
import operator


class RedditStrat:
    satoshi_50k = 0.0005

    def __init__(self, bittrex_api, reddit_api, total_slots):
        self.bittrex_api = bittrex_api
        self.reddit_api = reddit_api
        self.total_slots = total_slots

        self.bittrex_coins = utils.get_updated_bittrex_coins()

        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")

        self.initialize_reddit_coins()

    def reddit_buy_strat(self, total_bitcoin):
        return

    def reddit_sell_strat(self):
        return


    def initialize_reddit_coins(self):
        market_names = utils.get_bittrex_market_names()
        market_names['submissions'] = []
        utils.json_to_file(market_names, 'reddit_coins.json')

    def update_reddit_coins(self):
        reddit_coins = utils.file_to_json('reddit_coins.json')
        for submission in self.reddit_api.subreddit('CryptoCurrency').top('day'):
            if submission not in reddit_coins['submissions']:
                reddit_coins = self.find_mentions(submission.title, reddit_coins, str(submission), submission.created, submission.score)
                for comment in submission.comments:
                    reddit_coins = self.find_mentions(comment.body, reddit_coins, str(comment), comment.created, comment.score)
            reddit_coins['submissions'].append(str(submission))
        utils.json_to_file(reddit_coins, 'reddit_coins.json')

    def find_mentions(self, string, reddit_coins, mentioned_id, mentioned_time, upvotes):
        submissions = reddit_coins['submissions']
        del reddit_coins['submissions']
        for symbol in reddit_coins:
            full_name_reg = r"\b" + reddit_coins[symbol]['full_name'] + r"\b"
            symbol_reg = r"\b" + symbol + r"\b"
            if re.search(symbol_reg, string, re.IGNORECASE) or re.search(full_name_reg, string, re.IGNORECASE):
                reddit_coins[symbol]['mentioned_ids'].append(mentioned_id)
                reddit_coins[symbol]['mentioned_times'].append(mentioned_time)
                reddit_coins[symbol]['text'].append(string)
                reddit_coins[symbol]['upvotes'].append(upvotes)
        reddit_coins['submissions'] = submissions
        return reddit_coins

    def rank_by_mentions(self):
        reddit_coins = utils.file_to_json('reddit_coins.json')
        submissions = reddit_coins['submissions']
        del reddit_coins['submissions']
        ranked_coins = {}
        for coin in reddit_coins:
            ranked_coins[coin] = len(reddit_coins[coin]['mentioned_ids'])
        sorted_coins = sorted(ranked_coins.items(), key=operator.itemgetter(1), reverse=True)
        reddit_coins['submissions'] = submissions
        return sorted_coins

    def rank_by_upvotes(self):
        reddit_coins = utils.file_to_json('reddit_coins.json')
        submissions = reddit_coins['submissions']
        del reddit_coins['submissions']
        ranked_coins = {}
        for coin in reddit_coins:
            ranked_coins[coin] = sum(reddit_coins[coin]['upvotes'])
        sorted_coins = sorted(ranked_coins.items(), key=operator.itemgetter(1), reverse=True)
        reddit_coins['submissions'] = submissions
        return sorted_coins

    def refresh_held_pending(self):
        self.held_coins = utils.file_to_json("held_coins.json")
        self.pending_orders = utils.file_to_json("pending_orders.json")

    def update_bittrex_coins(self):
        self.bittrex_coins = utils.get_updated_bittrex_coins()