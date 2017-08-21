from Trader.bittrex3 import Bittrex3
import json
import urllib

with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    secrets_file.close()


api = Bittrex3(secrets['key'], secrets['secret'])