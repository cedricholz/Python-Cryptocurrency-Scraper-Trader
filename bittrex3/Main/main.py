from bittrex3.bittrex3 import Bittrex3
from forex_python.bitcoin import BtcConverter
import json


with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    secrets_file.close()

api = Bittrex3(secrets['key'], secrets['secret'])