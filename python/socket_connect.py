#!/usr/bin/env python3
import logging

from twisted.internet import reactor
#from moneysocket.socket.websocket import OutgoingWebsocketTransport

from moneysocket.socket.websocket import WebsocketInterconnect

def close_interconnect(interconnect):
    print("closing")
    interconnect.close()

def send_message(socket):
    print("sending")
    socket.write({"herp": "derp"})

def close_socket(socket):
    print("closing")
    socket.close()

def got_message(socket, msg):
    print("git msg: %s" % msg)
    #reactor.callLater(1.0, close_socket, socket)

def new_socket_cb(socket):
    print("got socket spawned: %s" % socket)
    socket.register_recv_cb(got_message)
    reactor.callLater(1.0, send_message, socket)

def socket_close_cb(uuid):
    print("got socket closed: %s" % uuid)

logging.basicConfig(level=logging.DEBUG)

wi = WebsocketInterconnect(new_socket_cb, socket_close_cb)

wi.connect("ws://localhost:9999")


reactor.callLater(5.0, close_interconnect, wi)
print("running reactor")
reactor.run()
