// resize header to size of browser window

var username = '';
var ready = (callback) => {
    if (document.readyState != "loading") callback();
    else document.addEventListener("DOMContentLoaded", callback);
}

ready(() => {
    document.querySelector(".header").style.height = window.innerHeight + "px";
})

// set modal time delay before loading

// setTimeout(function() {
// 	$('#demo-modal').modal();
// }, 500);

function parse_msg(socket_ch, msg) {
    console.log('socket : ', socket_ch)
    console.log('msg : ', msg)
    if (msg['status'] == 0) {
        for (const [key, value] of Object.entries(msg)) {
            if (msg != 'status' && msg != 'msg')
                $('#' + key).html(value);
        }
        switch (socket_ch) {
            case 'stream':
                $('#user').val(username);
                if (username != '') {
                    $("#positions_card").removeClass('invisible');
                    $("#open_trades_card").removeClass('invisible');
                }
                break;
            case 'user_load':
                username = msg['user'];
                iziToast.show({
                    theme: 'dark',
                    icon: 'icon-person',
                    title: 'Hey ' + msg['msg'],
                    message: 'Welcome!',
                    position: 'bottomRight', //'center', // bottomRight, bottomLeft, topRight, topLeft, topCenter, bottomCenter
                    progressBarColor: 'rgb(0, 255, 184)',
                    displayMode: 1,
                    onOpening: function(instance, toast) {
                        console.info('callback abriu!');
                    },
                    onClosing: function(instance, toast, closedBy) {
                        console.info('closedBy: ' + closedBy); // tells if it was closed by 'drag' or 'button'
                    }
                });
                socket.emit('stream', username);
                break;
            default:
                iziToast.info({
                    title: socket_ch,
                    message: msg['msg'],
                });
                break;
        }
    } else {
        iziToast.error({
            title: 'Error',
            message: msg['msg'],
            position: 'bottomRight',
        });
        username = '';
        $('#balance_V2').html('None');
        $('#user').html('Stream broken!<br>Need to Load user again!');
        $("#positions_card").addClass('invisible');
        $("#open_trades_card").addClass('invisible');
    }
}

var socket = io();
socket.on('connect', function() {
    iziToast.info({
        title: 'server',
        message: 'CONNECTED',
    });
});
socket.on('disconnect', function() {
    parse_msg('disconnect', { 'status': -1, 'msg': 'DISCONNECTED' });
});
socket.on('stream', function(msg) {
    parse_msg('stream', msg)
    socket.emit('stream', username);
});
socket.on('user_load', function(msg) {
    parse_msg('user_load', msg)
});

$(document).ready(function() {
    $('#load_nav').click(function() {
        socket.emit('user_load', $('#username').val());
    });
});