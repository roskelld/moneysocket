#!/usr/bin/env python3
import logging

from twisted.internet import reactor
from moneysocket.socket.websocket import IncomingWebsocketTransport

def socket_spawn(socket):
    print("got socket spawned: %s" % socket)

def socket_close(socket):
    print("got socket spawned: %s" % socket)


iwt = IncomingWebsocketTransport("0.0.0.0", 9999)

iwt.register_socket_spawn_cb(socket_spawn)
iwt.register_socket_close_cb(socket_close)

logging.basicConfig(level=logging.DEBUG)

print("running reactor")
reactor.run()
