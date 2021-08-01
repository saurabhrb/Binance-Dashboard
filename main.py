import pprint
import configparser
import logging
from datetime import date
import sys

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask import request

from Binance import BINANCE, Futures_position

rand_num = date.today().strftime("%d%m%Y%H%M%S")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def get_page():
    rule = request.url_rule
    print('\nROUTE : ' + str(rule.rule))
    print('')
    return render_template('index.html',rand_num=rand_num)

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('stream')
def test_send(data):
    emit('stream', {'status' : 0, 'msg' : '', 'user' : data, 'positions' : OBJs[data]['obj'].positions_html})
    socketio.sleep(300)

@socketio.on('user_load')
def test_user(data):
    data = data.lower()
    if data not in config:
        emit('user_load',{'status' : -1, 'msg' : "no keys found for user : '" + data + "'"})
    else:
      OBJs[data]={'api_key' : str(config[data]['API_KEY']), 'secret_key' : str(config[data]['SECRET_KEY'])}
      # try:
      OBJs[data]['obj'] = BINANCE(OBJs[data]['api_key'], OBJs[data]['secret_key'])
      obj = OBJs[data]['obj']
      balance_V2 = str(obj.get_balance_V2()) + ' USDT'
      # start and sign up sockets
      obj.start_webstream()
      open_trades = str(obj.get_open_trades())
      emit('user_load',{'status' : 0, 'msg' : "'" + data + "'", 'user' : data, 'table_heads' : Futures_position.html_tabel_head() , 'balance_V2' : str(balance_V2), 'open_trades' : open_trades})
      # except Exception as e:
      #   print(sys.exc_info()[2])
      #   emit('user_load',{'status' : -1, 'msg' : "could not create Binance object for user : '" + data + "'<br>" + str(sys.exc_info()[2])})

@app.route("/data/<path:path>")
def static_dir(path):
    path = path.replace(rand_num,"")
    return send_from_directory("data", path)

logger = logging.getLogger("binance-futures")
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

OBJs = {'saurabh' : None}
config = configparser.ConfigParser()
config.read('keys.cfg')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='localhost', port=8080)