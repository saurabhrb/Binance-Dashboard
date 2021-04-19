from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request

import pprint

import logging
from binance_f import RequestClient
from binance_f import SubscriptionClient
from binance_f.model import *
from binance_f.exception.binanceapiexception import BinanceApiException

from binance_f.base.printobject import *
import configparser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

obj = None

@app.route('/')
def get_page():
    rule = request.url_rule
    print('\nROUTE : ' + str(rule.rule))
    print('')
    return render_template('index.html')

@socketio.on('connect')
def test_connect():
    obj.get_balance_V2()
    obj.start_webstream()
    # print('')
    # print('')
    # # get current trades
    obj.get_open_trades()
    # print('')
    # print('')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('stream')
def test_send(data):
    # print(obj.positions_str)
    emit('stream', obj.positions_html)
    socketio.sleep(300)

# https://github.com/Binance-docs/Binance_Futures_python


g_account_id = 12345678

logger = logging.getLogger("binance-futures")
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# TODO inherit class Position
class Futures_position:
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
    # self.roe = 100 * (self.unrealizedProfit / self.isolatedMargin)

  def print(self):
    margin_ratio = self.margin_ratio
    roe = self.roe
    qty_str = str(self.positionAmt) + self.symbol.upper().split('USDT')[0]
    p = self.positionSide + ' ' + self.symbol.upper() + ' x' + str(self.leverage) + ' ' + qty_str + ' ' + str(self.entryPrice) + ' ' + str(self.markPrice) + ' ' + str(self.liquidationPrice) + ' ' + str(margin_ratio) + '% ' + str(self.isolatedMargin) + '(' + str(self.marginType) + ') ' + str(self.unrealizedProfit) + ' ' + str(roe) + '%'
    # print(p)
    return p
  
  def html_tabel_head(self):
    p = '''
    <tr>
        <th>Position</th>
        <th>Symbol</th>
        <th>Leverage</th>
        <th>Size</th>
        <th>Entry Price</th>
        <th>Mark Price</th>
        <th>Liq. Price</th>
        <th>Margin Ratio (TODO)</th>
        <th>Margin (TODO)</th>
        <th>PNL</th>
        <th>ROE% (TODO)</th>
    </tr>
    '''
    return p

  def html(self):
    margin_ratio = self.margin_ratio
    roe = self.roe
    qty_str = str(self.positionAmt) + ' ' + self.symbol.upper().split('USDT')[0]
    p = '''
    <tr>
        <td>''' + self.positionSide + '''</td>
        <td>''' + self.symbol.upper() + '''</td>
        <td>x''' + str(self.leverage) + '''</td>
        <td>''' + qty_str + '''</td>
        <td>''' + str(self.entryPrice) + '''</td>
        <td>''' + str(self.markPrice) + '''</td>
        <td>''' + str(self.liquidationPrice) + '''</td>
        <td>''' + str(margin_ratio) + '''%</td>
        <td>''' + str(self.isolatedMargin) + '''(''' + str(self.marginType) + ''')</td>
        <td>''' + str(self.unrealizedProfit) + '''</td>
        <td>''' + str(roe) + '''%</td>
    </tr>
    '''
    return p

class BINANCE:
  def __init__(self, api_key, secret_key):
    self.api_key = api_key
    self.secret_key = secret_key
    self.client = RequestClient(api_key=self.api_key, secret_key=self.secret_key)
    self.positions = {}
    self.balance = 0
    self.positions_str = ''
    self.positions_html = ''

  def update_position(self, event):
    if event.symbol.upper() in self.positions:
      self.positions[event.symbol.upper()].update_mark(event.markPrice, self.balance)

  def print_positions(self):
    self.positions_str = 'TODO: need to update Margin, Margin ratio and roe%\n'
    self.positions_html = '''<table style="width:100%; text-align: center" >'''
    print('')
    print('---------------------------------')
    k=1
    for symb in self.positions.keys():
      self.positions_str += str(k) + self.positions[symb].print() + '\n'
      if k == 1:
        self.positions_html += self.positions[symb].html_tabel_head()
      self.positions_html += self.positions[symb].html()
      k+=1
    print(self.positions_str)
    print('---------------------------------')
    print('')
    self.positions_html += '''
    </table>
    '''

  def get_listenkey(self):
    self.listen_key = self.client.start_user_data_stream()
    print("listenKey: ", self.listen_key)
  
  def start_webstream(self):
    # TODO, check if stream already started, end it and start a new one
    self.sub_client = None
    self.sub_client = SubscriptionClient(api_key=self.api_key,secret_key=self.secret_key)
    self.get_listenkey()
    self.sub_client.subscribe_user_data_event(self.listen_key, self.sub_callback, self.sub_error)
  
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
            print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
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
  
  def get_account_info_v2(self):
    result = self.client.get_account_information_v2()
    print("canDeposit: ", result.canDeposit)
    print("canWithdraw: ", result.canWithdraw)
    print("feeTier: ", result.feeTier)
    print("maxWithdrawAmount: ", result.maxWithdrawAmount)
    print("totalInitialMargin: ", result.totalInitialMargin)
    print("totalMaintMargin: ", result.totalMaintMargin)
    print("totalMarginBalance: ", result.totalMarginBalance)
    print("totalOpenOrderInitialMargin: ", result.totalOpenOrderInitialMargin)
    print("totalPositionInitialMargin: ", result.totalPositionInitialMargin)
    print("totalUnrealizedProfit: ", result.totalUnrealizedProfit)
    print("totalWalletBalance: ", result.totalWalletBalance)
    print("totalCrossWalletBalance: ", result.totalCrossWalletBalance)
    print("totalCrossUnPnl: ", result.totalCrossUnPnl)
    print("availableBalance: ", result.availableBalance)
    print("maxWithdrawAmount: ", result.maxWithdrawAmount)
    print("updateTime: ", result.updateTime)
    print("=== Assets ===")
    PrintMix.print_data(result.assets)
    print("==============")
    print("=== Positions ===")
    PrintMix.print_data(result.positions)
    print("==============")

  def get_account_info(self):
    result = self.client.get_account_information()
    print("canDeposit: ", result.canDeposit)
    print("canWithdraw: ", result.canWithdraw)
    print("feeTier: ", result.feeTier)
    print("maxWithdrawAmount: ", result.maxWithdrawAmount)
    print("totalInitialMargin: ", result.totalInitialMargin)
    print("totalMaintMargin: ", result.totalMaintMargin)
    print("totalMarginBalance: ", result.totalMarginBalance)
    print("totalOpenOrderInitialMargin: ", result.totalOpenOrderInitialMargin)
    print("totalPositionInitialMargin: ", result.totalPositionInitialMargin)
    print("totalUnrealizedProfit: ", result.totalUnrealizedProfit)
    print("totalWalletBalance: ", result.totalWalletBalance)
    print("updateTime: ", result.updateTime)
    print("=== Assets ===")
    PrintMix.print_data(result.assets)
    print("==============")
    print("=== Positions ===")
    PrintMix.print_data(result.positions)
    print("==============")

  def get_leverage_bracket(self):
    result = self.client.get_leverage_bracket()
    PrintMix.print_data(result)
  
  def get_balance(self):
    result = self.client.get_balance()
    PrintMix.print_data(result)
  
  # def __init__(self):
  #       self.accountAlias = ""
  #       self.asset = ""
  #       self.balance = 0.0
  #       self.crossWalletBalance = 0.0
  #       self.crossUnPnl = 0.0
  #       self.availableBalance = 0.0
  #       self.maxWithdrawAmount = 0.0
  def get_balance_V2(self):
    result = self.client.get_balance_v2()
    for res in result:
      if res.asset == "USDT":
        self.balance = res.balance
    print(self.balance)

  def change_initial_leverage(self, symbol,leverage):
    result = request_client.change_initial_leverage(symbol, leverage)
    PrintBasic.print_obj(result)

  def get_open_orders(self):
    result = self.client.get_open_orders()
    PrintMix.print_data(result)

  # def __init__(self):
  #   self.bracket = 0
  #   self.initialLeverage = 0
  #   self.notionalCap = 0.0
  #   self.notionalFloor = 0.0
  #   self.maintMarginRatio = 0.0
  #   self.cum = 0.0
  def get_leverage_bracket(self, symbol=''):
    result = self.client.get_leverage_bracket(symbol)
    PrintMix.print_data(result)
  
  def get_position(self):
    result = self.client.get_position()
    PrintMix.print_data(result)

  def get_position_v2(self, noprint=False):
    result = self.client.get_position_v2(noprint)
    # PrintMix.print_data(result)
    return result
  
  def get_open_trades(self):
    res = self.get_position_v2(True)
    print('------------')
    print(len(res))
    res2 = []
    lst_pairs = []
    for position in res:
      if position.positionAmt > 0:
        self.positions[position.symbol.upper()] = Futures_position(position)
        self.positions[position.symbol.upper()].print()
        lst_pairs.append(position.symbol)
        res2.append(position)
        # self.get_leverage_bracket(position.symbol)
    # PrintMix.print_data(res2)
    self.start_mark_price_ticker_stream(lst_pairs)

if __name__ == '__main__':  
  config = configparser.ConfigParser()
  config.read('keys.cfg')
  obj = BINANCE(str(config['KEYS']['API_KEY']), str(config['KEYS']['SECRET_KEY']))
  socketio.run(app)
