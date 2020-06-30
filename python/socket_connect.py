#!/usr/bin/env python3
import logging

from twisted.internet import reactor
from moneysocket.socket.websocket import OutgoingWebsocketTransport

def socket_spawn(socket):
    print("got socket spawned: %s" % socket)

def socket_close(socket):
    print("got socket spawned: %s" % socket)


owt = OutgoingWebsocketTransport()



owt.register_socket_spawn_cb(socket_spawn)
owt.register_socket_close_cb(socket_close)

owt.connect("ws://localhost:9999")

logging.basicConfig(level=logging.DEBUG)

print("running reactor")
reactor.run()
