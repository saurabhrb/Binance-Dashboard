from binance_f import RequestClient, SubscriptionClient
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.base.printobject import *
from binance_f.model import *

def debug(func=None):
    def wrapper(*args, **kwargs):
        try:
            function_name = func.__func__.__qualname__
        except:
            function_name = func.__qualname__
        print(function_name + '() -->')
        res = func(*args, **kwargs)
        print('<-- ' + function_name + '()')
        return res
    return wrapper

# TODO inherit class Position
class Futures_position(Position):
    # def __init__(self,position):
    #     super().__init__()
    #     self.roe = 0
    #     self.margin_ratio = 0
    def __init__(self):
      self.entryPrice = 0.0
      self.isAutoAddMargin = False
      self.leverage = 0.0
      self.maxNotionalValue = 0.0
      self.liquidationPrice = 0.0
      self.markPrice = 0.0
      self.positionAmt = 0.0
      self.symbol = ""
      self.unrealizedProfit = 0.0
      self.marginType = ""
      self.isolatedMargin = 0.0
      self.positionSide = ""

      self.roe = 0
      self.margin_ratio = 0
    
    def __init__(self, position):
      self.entryPrice = position.entryPrice
      self.isAutoAddMargin = position.isAutoAddMargin
      self.leverage = position.leverage
      self.maxNotionalValue = position.maxNotionalValue
      self.liquidationPrice = position.liquidationPrice
      self.markPrice = position.markPrice
      self.positionAmt = position.positionAmt
      self.symbol = position.symbol
      self.unrealizedProfit = position.unrealizedProfit
      self.marginType = position.marginType
      self.isolatedMargin = position.isolatedMargin
      self.positionSide = position.positionSide

      self.roe = 0
      self.margin_ratio = 0
    
    def update_mark(self, markPrice, balance):
        self.markPrice = markPrice
        self.unrealizedProfit = self.positionAmt * (self.markPrice - self.entryPrice)
        if self.positionSide == 'SHORT':
          self.unrealizedProfit = -1 * self.unrealizedProfit
        if self.isolatedMargin != 0:
          self.roe = 100 * (self.unrealizedProfit / self.isolatedMargin)

    def print(self):
        qty_str = ('%.3f' % self.positionAmt) + self.symbol.upper().split('USDT')[0] + '(' + ('%.3f' % (self.positionAmt * self.markPrice)) + 'USDT)'
        if self.unrealizedProfit > 0:
          PNL = '+' + ('%.3f' % self.unrealizedProfit) + ' USDT '
        else:
          PNL = ('%.3f' % self.unrealizedProfit) + ' USDT '
        if self.roe > 0:
          ROE = '+' + ('%.3f' % self.roe) + '%'
        else:
          ROE = ('%.3f' % self.roe) + '%'

        p = self.positionSide + ' ' + self.symbol.upper() + ' x' + ('%d' % self.leverage) + ' ' + qty_str + ' ' + ('%.3f' % self.entryPrice) + ' ' + ('%.3f' % self.markPrice) + ' ' + ('%.3f' % self.liquidationPrice) + ' ' + ('%.3f' % self.margin_ratio) + '% ' + ('%.3f' % self.isolatedMargin) + '(' + str(self.marginType) + ') ' + PNL + ROE
        return p
        
    @staticmethod
    def html_tabel_head():
        p = '''
        <tr>
            <th>Position</th>
            <th>Symbol</th>
            <th>Leverage</th>
            <th>Size</th>
            <th>Entry Price</th>
            <th>Mark Price</th>
            <th>Liq. Price</th>
            <th>Margin Ratio%</th>
            <th>Margin</th>
            <th>PNL</th>
            <th>ROE%</th>
        </tr>
        '''
        return p

    def html(self):
        qty_str = ('%.3f' % self.positionAmt) + ' ' + self.symbol.upper().split('USDT')[0] + ' (' + ('%.3f' % (self.positionAmt * self.markPrice)) + ' USDT)'
        if self.unrealizedProfit > 0:
          PNL = '+' + ('%.3f' % self.unrealizedProfit) + ' USDT '
        else:
          PNL = ('%.3f' % self.unrealizedProfit) + ' USDT '
        if self.roe > 0:
          ROE = '+' + ('%.3f' % self.roe) + '%'
        else:
          ROE = ('%.3f' % self.roe) + '%'
        p = '''
        <tr>
            <td>''' + self.positionSide + '''</td>
            <td>''' + self.symbol.upper() + '''</td>
            <td>''' + ('%d' % self.leverage) + '''x</td>
            <td>''' + qty_str + '''</td>
            <td>''' + ('%.3f' % self.entryPrice) + ''' USDT</td>
            <td>''' + ('%.3f' % self.markPrice)+ ''' USDT</td>
            <td>''' + ('%.3f' % self.liquidationPrice) + ''' USDT</td>
            <td>''' + ('%.3f' % self.margin_ratio) + '''%</td>
            <td>''' + ('%.3f' % self.isolatedMargin) + ''' USDT (''' + str(self.marginType) + ''')</td>
            <td>''' + PNL  + '''</td>
            <td>''' + ROE + '''</td>
        </tr>
        '''
        return p

class BINANCE:
  def __init__(self, api_key, secret_key):
    self.api_key = api_key
    self.secret_key = secret_key
    self.client = RequestClient(api_key=self.api_key, secret_key=self.secret_key)
    self.positions = {}
    self.assets = {}
    self.balance = 0
    self.positions_str = ''
    self.positions_html = ''

  @debug
  def update_position(self, event):
    if event.symbol.upper() in self.positions:
      self.positions[event.symbol.upper()].update_mark(event.markPrice, self.balance)

  @debug
  def print_positions(self):
    self.positions_str = ''
    self.positions_html = '''<table style="width:100%; text-align: center" >'''
    print('---------------------------------')
    k=1
    for symb in self.positions.keys():
      if k!=1:
        self.positions_str += '\n'
      self.positions_str += str(k) + self.positions[symb].print()
      self.positions_html += self.positions[symb].html()
      k+=1
    print(self.positions_str)
    print('---------------------------------')
    self.positions_html += '''
    </table>
    '''

  @debug
  def get_listenkey(self):
    self.listen_key = self.client.start_user_data_stream()
  
  @debug
  def start_webstream(self):
    # TODO : check if stream already running and close if already running
    # if self.sub_client != None:
    #   self.sub_client.unsubscribe_all()
    #   self.sub_client = None
    self.sub_client = None
    self.sub_client = SubscriptionClient(api_key=self.api_key,secret_key=self.secret_key)
    self.get_listenkey()
    self.sub_client.subscribe_user_data_event(self.listen_key, self.sub_callback, self.sub_error)
  
  @debug
  def start_mark_price_ticker_stream(self, lst_pairs=[]):
    for pairs in lst_pairs:
      self.sub_client.subscribe_mark_price_event(pairs.lower(), self.sub_callback, self.sub_error)

  def sub_callback(self, data_type: 'SubscribeMessageType', event: 'any'):
    if data_type == SubscribeMessageType.RESPONSE:
        print("Event ID: ", event)
    elif  data_type == SubscribeMessageType.PAYLOAD:
        if(event.eventType == "ACCOUNT_UPDATE"):
            print("Event Type: ", event.eventType)
            print("Event time: ", event.eventTime)
            # print("Transaction time: ", event.transactionTime)
            # print("=== Balances ===")
            # PrintMix.print_data(event.balances)
            # print("================")
            # print("=== Positions ===")
            # PrintMix.print_data(event.positions)
            # print("================")
        elif(event.eventType == "ORDER_TRADE_UPDATE"):
            print("Event Type: ", event.eventType)
            print("Event time: ", event.eventTime)
            # print("Transaction Time: ", event.transactionTime)
            # print("Symbol: ", event.symbol)
            # print("Client Order Id: ", event.clientOrderId)
            # print("Side: ", event.side)
            # print("Order Type: ", event.type)
            # print("Time in Force: ", event.timeInForce)
            # print("Original Quantity: ", event.origQty)
            # print("Position Side: ", event.positionSide)
            # print("Price: ", event.price)
            # print("Average Price: ", event.avgPrice)
            # print("Stop Price: ", event.stopPrice)
            # print("Execution Type: ", event.executionType)
            # print("Order Status: ", event.orderStatus)
            # print("Order Id: ", event.orderId)
            # print("Order Last Filled Quantity: ", event.lastFilledQty)
            # print("Order Filled Accumulated Quantity: ", event.cumulativeFilledQty)
            # print("Last Filled Price: ", event.lastFilledPrice)
            # print("Commission Asset: ", event.commissionAsset)
            # print("Commissions: ", event.commissionAmount)
            # print("Order Trade Time: ", event.orderTradeTime)
            # print("Trade Id: ", event.tradeID)
            # print("Bids Notional: ", event.bidsNotional)
            # print("Ask Notional: ", event.asksNotional)
            # print("Is this trade the maker side?: ", event.isMarkerSide)
            # print("Is this reduce only: ", event.isReduceOnly)
            # print("stop price working type: ", event.workingType)
            # print("Is this Close-All: ", event.isClosePosition)
            # if not event.activationPrice is None:
            #     print("Activation Price for Trailing Stop: ", event.activationPrice)
            # if not event.callbackRate is None:
            #     print("Callback Rate for Trailing Stop: ", event.callbackRate)
            self.update_position(event)
        elif(event.eventType == "listenKeyExpired"):
            print("Event: ", event.eventType)
            print("Event time: ", event.eventTime)
            print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
        elif(event.eventType == "markPriceUpdate"):
            # print("Event: ", event.eventType)
            # print("Event time: ", event.eventTime)
            # PrintBasic.print_obj(event)
            self.update_position(event)
        else:
            print("Event: ", event.eventType)
            print("Event time: ", event.eventTime)
            # PrintBasic.print_obj(event)
        self.print_positions()
    else:
        print("Unknown Data:")
    print()

  def sub_error(self, e: 'BinanceApiException'):
    print(e.error_code + e.error_message)
  
  @debug
  def get_account_info_v2(self):
    print('------------')
    result = self.client.get_account_information_v2()
    print('------------')
    if result.totalMarginBalance > 0:
      margin_ratio = (result.totalMaintMargin/result.totalMarginBalance)*100
    else:
      margin_ratio = 0.0
    # print("canDeposit: ", result.canDeposit)
    # print("canWithdraw: ", result.canWithdraw)
    # print("feeTier: ", result.feeTier)
    # print("maxWithdrawAmount: ", result.maxWithdrawAmount)
    # print("totalInitialMargin: ", result.totalInitialMargin)
    # print("totalMaintMargin: ", result.totalMaintMargin)
    # print("totalMarginBalance: ", result.totalMarginBalance)
    # print("totalOpenOrderInitialMargin: ", result.totalOpenOrderInitialMargin)
    # print("totalPositionInitialMargin: ", result.totalPositionInitialMargin)
    # print("totalUnrealizedProfit: ", result.totalUnrealizedProfit)
    # print("totalWalletBalance: ", result.totalWalletBalance)
    # print("totalCrossWalletBalance: ", result.totalCrossWalletBalance)
    # print("totalCrossUnPnl: ", result.totalCrossUnPnl)
    # print("availableBalance: ", result.availableBalance)
    # print("maxWithdrawAmount: ", result.maxWithdrawAmount)
    # print("updateTime: ", result.updateTime)
    # print("=== Assets ===")
    # PrintMix.print_data(result.assets)
    for asset in result.assets:
      if asset.availableBalance > 0:
        self.assets[asset.asset.upper()] = asset
    for position in result.positions:
      if position.symbol.upper() in self.positions and self.positions[position.symbol.upper()].positionSide == position.positionSide:
        self.positions[position.symbol.upper()].margin_ratio = margin_ratio
        self.positions[position.symbol.upper()].isolatedMargin = position.positionInitialMargin
  
  @debug
  def get_balance(self):
    result = self.client.get_balance()
    # PrintMix.print_data(result)
    return result
  
  @debug
  def get_balance_V2(self):
    result = self.client.get_balance_v2()
    for res in result:
      if res.asset == "USDT":
        self.balance = res.balance
    return self.balance

  @debug
  def get_leverage_bracket(self, symbol=''):
    result = self.client.get_leverage_bracket(symbol)
    # PrintMix.print_data(result)
    return result
  
  @debug
  def get_position(self):
    result = self.client.get_position()
    # PrintMix.print_data(result)
    return result

  @debug
  def get_position_v2(self):
    result = self.client.get_position_v2()
    # PrintMix.print_data(result)
    return result
  
  @debug
  def get_open_trades(self):
    print('------------')
    res = self.get_position_v2()
    print('------------')
    print('')
    print('Total open trades : ' + str(len(res)))
    res2 = []
    lst_pairs = []
    for position in res:
      if position.positionAmt > 0:
        self.positions[position.symbol.upper()] = Futures_position(position)
        self.positions[position.symbol.upper()].print()
        lst_pairs.append(position.symbol)
        res2.append(position)
        PrintMix.print_data(position)
        # self.get_leverage_bracket(position.symbol)

    # get margin values of orders and assets
    self.get_account_info_v2()

    self.start_mark_price_ticker_stream(lst_pairs)
    return lst_pairs
  
  @debug
  def get_position_margin_change_history(self, symbol):
    result = self.client.get_position_margin_change_history(symbol=symbol)
    PrintBasic.print_obj(result)

  @debug
  def get_account_trades(self,symbol):
    result = self.client.get_account_trades(symbol=symbol)
    PrintMix.print_data(result)
  
  # class LeverageBracket:
  #   def __init__(self):
  #       self.symbol = ""
  #       self.brackets = list()
  # class Bracket:
  #   def __init__(self):
  #       self.bracket = 0
  #       self.initialLeverage = 0
  #       self.notionalCap = 0.0
  #       self.notionalFloor = 0.0
  #       self.maintMarginRatio = 0.0
  #       self.cum = 0.0
  @debug
  def get_leverage_bracket(self, symbol, lev):
    result = self.client.get_leverage_bracket()
    for res in result:
      if res.symbol == symbol:
        for l in res.brackets:
          if l.initialLeverage == lev:
            PrintMix.print_data(l)
          break
    return result

  @debug
  def get_order(self, symbol, orderid):
    result = self.client.get_order(symbol=symbol, orderId=orderid)
    PrintBasic.print_obj(result)