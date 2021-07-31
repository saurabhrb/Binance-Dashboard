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