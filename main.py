import pprint
import configparser
import logging
from datetime import date
import sys
from subprocess import call

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask import request

from Binance import BINANCE, Futures_position
from binance_f.base.printobject import *

rand_num = date.today().strftime("%d%m%Y%H%M%S")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', async_handlers=True)

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
    if data in OBJs:
        emit('stream', {'status' : 0, 'msg' : '', 'user' : data, 'positions' : OBJs[data]['obj'].positions_html})
    socketio.sleep(300)

@socketio.on('user_load')
def test_user(data):
    data = data.lower()
    if data not in config:
        emit('user_load',{'status' : -1, 'msg' : "no keys found for user : '" + data + "'", 'user' : data})
    else:
        OBJs[data]={'api_key' : str(config[data]['API_KEY']), 'secret_key' : str(config[data]['SECRET_KEY'])}
        try:
            OBJs[data]['obj'] = BINANCE(OBJs[data]['api_key'], OBJs[data]['secret_key'])
            obj = OBJs[data]['obj']
            balance_V2 = ('%.3f' % obj.get_balance_V2()) + ' USDT'
            # start and sign up sockets
            obj.start_webstream()
            open_trades = str(obj.get_open_trades())
            assets = str(obj.assets)
            emit('user_load',{'status' : 0, 'msg' : "'" + data + "'", 'user' : data, 'table_heads' : Futures_position.html_tabel_head() , 'balance_V2' : str(balance_V2), 'open_trades' : open_trades + '<br>' + assets})
        except:
            print(sys.exc_info()[2])
            emit('user_load',{'status' : -1, 'msg' : "could not create Binance object for user : '" + data + "'<br>" + str(sys.exc_info()[2])})

@app.route("/data/<path:path>")
def static_dir(path):
    path = path.replace(rand_num,"")
    return send_from_directory("data", path)

logger = logging.getLogger("binance-futures")
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

OBJs = {}
config = configparser.ConfigParser()
config.read('keys.cfg')

def debug():
    obj = BINANCE(str(config['saurabh']['API_KEY']), str(config['saurabh']['SECRET_KEY']))
    balance_V2 = str(obj.get_balance_V2()) + ' USDT'
    open_trades = str(obj.get_open_trades())
    assets = str(obj.assets)
    positions = obj.positions
    print(balance_V2)
    print(open_trades)


def main():
    print('Running setup.sh')
    with open('setup.sh', 'r') as file:
        script = file.read()
    rc = call(script, shell=True)
    print(rc)
    print('')
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()
    # debug()
