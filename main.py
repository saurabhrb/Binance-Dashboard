from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask import request

import pprint
import configparser
import logging

from binance_f import RequestClient, SubscriptionClient
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.base.printobject import *
from binance_f.model import *

import Binance

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def get_page():
    rule = request.url_rule
    print('\nROUTE : ' + str(rule.rule))
    print('')
    return render_template('index.html')

@socketio.on('connect')
def test_connect():
    # obj.get_balance_V2()
    # obj.start_webstream()
    print('connect')
    emit('stream',0)
    # print('')
    # # get current trades
    # obj.get_open_trades()
    # print('')
    # print('')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('stream')
def test_send(data):
    # print(obj.positions_str)
    # emit('stream', obj.positions_html)
    emit('stream',int(data)+1)
    socketio.sleep(300)

@app.route("/data/<path:path>")
def static_dir(path):
    return send_from_directory("data", path)

logger = logging.getLogger("binance-futures")
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


if __name__ == '__main__':
  socketio.run(app, host='0.0.0.0', port=8080)