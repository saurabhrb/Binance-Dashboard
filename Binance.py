from binance_f import RequestClient, SubscriptionClient
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.base.printobject import *
from binance_f.model import *

class BINANCE:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.client = RequestClient(api_key=self.api_key, secret_key=self.secret_key)
        self.positions = {}
        self.balance = 0
        self.positions_str = ''
        self.positions_html = ''
        # self.g_account_id = 12345678
        print(api_key)
        print(secret_key)

    def get_balance_V2(self):
        result = self.client.get_balance_v2()
        for res in result:
            if res.asset == "USDT":
                self.balance = res.balance
        PrintMix.print_data(self.balance)
        return self.balance