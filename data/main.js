// resize header to size of browser window

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
    if (msg['status'] == 0) {
        switch (socket_ch) {
            case 'user_load':
                for (const [key, value] of Object.entries(msg)) {
                    if (msg != 'status' && msg != 'msg')
                        $('#' + key).innerHTML(value);
                }
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
                break;
            default:
                iziToast.info({
                    title: socket_ch,
                    message: msg['msg'],
                });
                break;
        }
    } else
        iziToast.error({
            title: 'Error',
            message: msg['msg'],
            position: 'bottomRight',
        });
}

var socket = io();
socket.on('connect', function() {
    iziToast.info({
        title: 'server',
        message: 'CONNECTED',
    });
});
socket.on('disconnect', function() {
    iziToast.error({
        title: 'server',
        message: 'DISCONNECTED',
    });
});
// socket.on('stream', function(msg) {
//     socket.emit('stream', '1');
// });
socket.on('user_load', function(msg) {
    parse_msg('user_load', msg)
});

$(document).ready(function() {
    $('#load_nav').click(function() {
        socket.emit('user_load', $('#username').val());
    });
});