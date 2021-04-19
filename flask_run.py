global_variables = {}
server_variables = {}
flask_config = {}
route_variables = {}

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty # for Python 3.x


import ctypes

import threading
import webbrowser
from threading import Thread, Event, Timer
import time
import subprocess
import random
import atexit
import os
import sys
import platform
from ansi2html import Ansi2HTMLConverter
import re


# returns OS name
def get_platform_name():
    if platform.mac_ver()[0]:
        return 'mac'
    if platform.win32_ver()[0]:
        return 'windows'
    if any(platform.dist()):
        return 'unix'
    if platform.java_ver()[0] or platform.java_ver()[1]:
        return 'java'
    return 'unknown OS'

########################################################
# GLOBALS
global_variables['current_path'] = os.getcwd()
global_variables['client_num'] = 1
print("Current Path = " + str(global_variables['current_path']))

global_variables['OS'] = get_platform_name()

global_variables['conv'] = Ansi2HTMLConverter()
global_variables['ansi_escape'] = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
########################################################

if (sys.version_info > (3, 0)):
    def unicode_or_str(msg):
        return str(msg)
else:
    def unicode_or_str(msg):
        return unicode(msg)

import flask
from flask import flash, redirect, render_template, request, session, abort, url_for, send_from_directory, jsonify, stream_with_context
from flask_socketio import SocketIO, join_room, leave_room, emit



THREAD = Thread()

########################################################
# FLASK configuration
flask_config['host'] = "my_FLASK_LiveTerminal.com"

app = flask.Flask(__name__)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'
SOCKETIO = SocketIO()
SOCKETIO.init_app(app, async_mode='eventlet', async_handlers=True)
########################################################


########################################################
## HELPERS

# queue push function
def enqueue_output(out, queue):
    try:
        for _line in iter(out.readline, b''):
            queue.put(_line)
    except:
        pass

class dummy:
    pid = ''

# shuts down flask socketio server
def shutdown_server():
    SOCKETIO.stop()
    print("SERVER CLOSED!")

# returns location of host file
def hosts_file(os):
    return {
        'mac': '/private/etc/hosts',
        'windows': 'c:\\Windows\\System32\\Drivers\\etc\\hosts',
        'unix' : 3
    }.get(os, 'XXX')

# simple if string is an integer check function
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

########################################################


########################################################
# FLASK ROUTES
route_variables['jquery_script_path1'] = '/static/jquery-1.4.2.min.js'
route_variables['jquery_script_path2'] = '/static/socket.io.min.js'
route_variables['img_url'] = '/static/pyNUT_background.jpg'
route_variables['style_url'] = '/static/style.css'
route_variables['shutdown'] = 0

# route for webpage icon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico',mimetype='static/favicon.ico')

# route for main page, /home page
@app.route('/home')
def get_page():
    rule = request.url_rule
    print('\nROUTE : ' + str(rule.rule))
    print('')
    return flask.render_template('home.html',route_variables=route_variables)

## SERVER SHUTDOWN ROUTES

# route to signal shutdown of FLASK server
@app.route('/shutdown')
def shutdown_initiate():
    rule = request.url_rule
    print('\nROUTE : ' + str(rule.rule))
    route_variables['shutdown'] = 1
    print('')
    return render_template('home.html',route_variables=route_variables)

# route to shutdown FLASK server
@app.route('/shut_me')
def shut_me_now():
    rule = request.url_rule
    print('\nROUTE : ' + str(rule.rule))
    shutdown_server()
    print('')
    return "SERVER CLOSED!"

########################################################



########################################################
# SOCKET ROUTES

# route for socket connection
@SOCKETIO.on('connect', namespace='/test')
def test_connect():
    if request.sid not in server_variables.keys():
        server_variables[request.sid] = {'sid' : request.sid, 'stats' : 'connected', 'dummy_pid' : 1, 'cmds': [], 'client_num' : global_variables['client_num']}
        global_variables['client_num'] = global_variables['client_num'] + 1
    print(str(request.sid) + '=> Client Connected <- ' + str(server_variables[request.sid]['client_num']))

# route for socket disconnection
@SOCKETIO.on('disconnect', namespace='/test')
def test_disconnect():
    if request.sid in server_variables.keys():
        server_variables[request.sid]['stats'] = 'disconnected'
    print(str(request.sid) + '=> Client Disconnected <- ' + str(server_variables[request.sid]['client_num']))

# route to receive stdin to supply to terminal
@SOCKETIO.on('send_com2', namespace='/test')
def send_com(cmd):
    if cmd is not None and cmd != "":
        print(str(server_variables[request.sid]['client_num']) + '=> SEND INPUT: ' + str(cmd))
        if 'proc' in server_variables[request.sid].keys() and  server_variables[request.sid]['proc']:
            try:
                server_variables[request.sid]['proc'].stdin.write(str(str(cmd) + '\n'))
                server_variables[request.sid]['proc'].stdin.flush()
            except :
                # emit('new_process',{'pid' : str(proc.pid)}))
                if 'proc' in server_variables[request.sid].keys() and server_variables[request.sid]['proc']:
                    print(str(server_variables[request.sid]['client_num']) + '=> closing prev process')
                    try:
                        server_variables[request.sid]['proc'].stdout.close()
                        print(str(server_variables[request.sid]['client_num']) + "=> closed stdout")
                    except:
                        print(str(server_variables[request.sid]['client_num']) + '=> cannot close stdout')
                    try:
                        server_variables[request.sid]['proc'].stdin.close()
                        print(str(server_variables[request.sid]['client_num']) + "=> closed stdin")
                    except:
                        print(str(server_variables[request.sid]['client_num']) + '=> cannot close stdin')
                    try:
                        server_variables[request.sid]['proc'].terminate()
                        print(str(server_variables[request.sid]['client_num']) + "=> closed proc")
                    except:
                        print(str(server_variables[request.sid]['client_num']) + '=> cannot close proc')
                server_variables[request.sid]['proc'] = dummy()
                print(str(server_variables[request.sid]['client_num']) + "=> STREAMING STOPPED")
                emit('my response', {'data': 'STOPPED', 'pid': server_variables[request.sid]['proc'].pid, 'stats': 'STOPPED'})

                ex_type, ex, tb = sys.exc_info()
                print(str(server_variables[request.sid]['client_num']) + "=> Unexpected error:", str(ex))
                # print('ERR: ' + str(e))
                # print("STREAMING STOPPED")
                emit('my response', {'data': "Unexpected error: " + str(ex), 'pid': server_variables[request.sid]['proc'].pid, 'stats': 'STOPPED'})
    else:
        print(str(server_variables[request.sid]['client_num']) + '=> NONE RECEIVED!')

@SOCKETIO.on('stop_stream', namespace='/test')
def stop_streaming():
    # emit('new_process',{'pid' : str(proc.pid)}))
    if 'proc' in server_variables[request.sid].keys() and server_variables[request.sid]['proc']:
        print(str(server_variables[request.sid]['client_num']) + '=> closing prev process')
        try:
            server_variables[request.sid]['proc'].stdin.close()
            print(str(server_variables[request.sid]['client_num']) + "=> closed stdin")
        except:
            print(str(server_variables[request.sid]['client_num']) + '=> cannot close stdin')
        try:
            server_variables[request.sid]['proc'].terminate()
            print(str(server_variables[request.sid]['client_num']) + "=> closed proc")
        except:
            print(str(server_variables[request.sid]['client_num']) + '=> cannot close proc')

        server_variables[request.sid]['proc'] = dummy()
        print(str(server_variables[request.sid]['client_num']) + "=> STREAMING STOPPED")
        emit('my response', {'data': 'STOPPED', 'pid': server_variables[request.sid]['proc'].pid, 'stats': 'STOPPED'})

@SOCKETIO.on('custom', namespace='/test')
def custom_socket():
    print(str(server_variables[request.sid]['client_num']) + '=> custom socket')

@SOCKETIO.on('stream', namespace='/test')
def connect_socket2(cmd):
    print(str(server_variables[request.sid]['client_num']) + '=> STREAMING')
    # emit('new_process',{'pid' : str(proc.pid)}))
    if 'proc' in server_variables[request.sid].keys() and server_variables[request.sid]['proc']:
        print(str(server_variables[request.sid]['client_num']) + '=> closing prev process')
        try:
            server_variables[request.sid]['proc'].stdout.close()
            print(str(server_variables[request.sid]['client_num']) + "=> closed stdout")
        except:
            print(str(server_variables[request.sid]['client_num']) + '=> cannot close stdout')
        try:
            server_variables[request.sid]['proc'].stdin.close()
            print(str(server_variables[request.sid]['client_num']) + "=> closed stdin")
        except:
            print(str(server_variables[request.sid]['client_num']) + '=> cannot close stdin')
        try:
            server_variables[request.sid]['proc'].terminate()
            print(str(server_variables[request.sid]['client_num']) + "=> closed proc")
        except:
            print(str(server_variables[request.sid]['client_num']) + '=> cannot close proc')

    server_variables[request.sid]['proc'] = dummy()
    server_variables[request.sid]['cmds'].append(str(cmd))

    if 'cd ' in cmd or 'CD ' in cmd:
        server_variables[request.sid]['dummy_pid'] = server_variables[request.sid]['dummy_pid'] + 1
        emit('new_process',{'pid' : str(server_variables[request.sid]['dummy_pid'])})
        if 'cd ' in cmd:
            path = str(cmd.split('cd ')[1])
        else:
            path = str(cmd.split('CD ')[1])

        if os.path.isdir(str(path)):
            os.chdir(path)
            emit('my response', {'data': 'Directory changed to ' + path, 'pid': server_variables[request.sid]['dummy_pid'], 'stats' : 'DONE'})
        else:
            emit('my response', {'data': 'Invalid path: ' + path, 'pid': server_variables[request.sid]['dummy_pid'], 'stats' : 'DONE'})
            # SOCKETIO.sleep(0)
        return

    try:
        proc = subprocess.Popen(cmd.split(' '),stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    except :
        ex_type, ex, tb = sys.exc_info()
        print(str(server_variables[request.sid]['client_num']) + "=> Unexpected error:", str(ex))
        server_variables[request.sid]['dummy_pid'] = server_variables[request.sid]['dummy_pid'] + 1
        emit('new_process',{'pid' : str(server_variables[request.sid]['dummy_pid'])})
        emit('my response', {'data': "Unexpected error: " + str(ex), 'pid': str(server_variables[request.sid]['dummy_pid']), 'stats': 'STOPPED'})
        return

    q = Queue()
    t1 = Thread(target=enqueue_output, args=(proc.stdout, q)) 
    t1.daemon = True
    t1.start()
    emit('new_process',{'pid' : str(proc.pid)})
    server_variables[request.sid]['proc'] = proc
    while True:
        line = ''
        if server_variables[request.sid]['proc'].pid != proc.pid:
            print(str(server_variables[request.sid]['client_num']) + "=> CLOSED PREV STREAM")
            break
        try:
            line = q.get_nowait()
        except Empty:
            pass
        else:
            line = line.strip('\t')
            line = line.strip('\n')
            #COLOR OUTPUT
            try:
                html_line = global_variables['conv'].convert(line)
                html_line = str(html_line).replace('<pre class="ansi2html-content">','<pre class="ansi2html-content" style="color: #ffffffb3; background-color: rgba(0, 0, 0, 0);border:0;">')
            except:
                html_line = line
            emit('my response', {'data': html_line, 'pid': proc.pid,'stats' : 'RUNNING'})
        if proc.poll() is not None:
            for i in range(0,q.qsize()):
                line = q.get_nowait()
                line = line.strip('\t')
                line = line.strip('\n')
                #COLOR OUTPUT
                try:
                    html_line = global_variables['conv'].convert(line)
                    html_line = str(html_line).replace('<pre class="ansi2html-content">','<pre class="ansi2html-content" style="color: #ffffffb3; background-color: rgba(0, 0, 0, 0);border:0;">')
                except:
                    html_line = line                
                emit('my response', {'data': html_line, 'pid': proc.pid,'stats' : 'RUNNING'})
            try:
                emit('my response', {'data': html_line, 'pid': proc.pid, 'stats' : 'DONE'})
            except:
                pass
            print(str(server_variables[request.sid]['client_num']) + '=> FINISHED STREAM')
            break

        SOCKETIO.sleep(0)

########################################################


## HOST CHECK
def check_hosts_exists():
    print('HOST_CHECK -> ' + str(flask_config['host']))
    import socket
    from socket import gethostbyname, gaierror
    try:
        socket.gethostbyname(str(flask_config['host']))
        print("HOST ALREADY PRESENT")
        return 1
    except :
        print("HOST NOT FOUND!\nADDING THE HOST TO HOSTS FILE")
        print('curr dir: ' + str(os.getcwd()))
        if global_variables['OS'] == 'mac':
            os.system('sudo python host_check.py ' + flask_config['host'] + ' ' + hosts_file('mac'))
        elif global_variables['OS'] == 'windows':
            print(sys.executable)
            print(str(os.getcwd()) + os.sep + 'host_check.py ' + flask_config['host'] + ' ' + hosts_file('windows'))
            ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode_or_str(sys.executable), unicode_or_str('host_check.py ' + flask_config['host'] + ' ' + hosts_file('windows')), None, 1)
            print('ran_win')
        return 0
########################################################

## EXIT PROCEDURE
def exit_handler():
    print('\n\nClients:\n')
    print('---------------------------------------------------------------')
    # import pprint
    # for sid in server_variables.keys():
    #     pprint.pprint(server_variables[sid],width = 1)
    #     print('')
    for sid in server_variables.keys():
        for k in server_variables[sid].keys():
            print(str(k) + ': ' + str(server_variables[sid][k]))
        print('---------------------------------------------------------------')
        print('')

    print('Live Terminal CLosed!')
    # print('Press any key to exit terminal')

atexit.register(exit_handler)
########################################################

## MAIN
if __name__ == "__main__":
    #check if host already added
    if check_hosts_exists() == 0:
        print("Close this terminal and re-run the executable")
        sys.exit(0)
    
    try:
        my_port = sys.argv[1]
    except:
        my_port = 5000

    if len(sys.argv)> 2 and sys.argv[2] == 'debug':
        deb = True
    else:
        deb = False

    #the web url
    print("SITE URL : " + 'http://' + str(flask_config['host']) + ':' + str(my_port) + '/home')

    #open web browser
    threading.Timer(1.25, lambda: webbrowser.open('http://' + str(flask_config['host']) + ':' + str(my_port) + '/home') ).start()

    #run flask app
    SOCKETIO.run(app,port=my_port,debug=deb)
########################################################