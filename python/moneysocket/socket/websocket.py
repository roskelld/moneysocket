# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import logging
import uuid
import json

from OpenSSL import SSL

from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import listenWS
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.websocket import WebSocketServerProtocol

from autobahn.twisted.websocket import connectWS
from autobahn.twisted.websocket import WebSocketClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol

from moneysocket.socket.socket import MoneysocketSocket, MoneysocketInterconnect


class WebsocketInterconnect(MoneysocketInterconnect):
    def __init__(self, new_socket_cb, socket_close_cb):
        super().__init__(new_socket_cb, socket_close_cb)
        self.incoming = []
        self.outgoing = []

    def listen(self, bind, port, use_tls=None):
        i = IncomingWebsocketInterconnect(self._new_socket, self._socket_close)
        self.incoming.append(i)
        i.listen(bind, port, use_tls=use_tls)

    def connect(self, url):
        print("connecT")
        o = OutgoingWebsocketInterconnect(self._new_socket, self._socket_close)
        self.outgoing.append(o)
        o.connect(url)

    def initiate_close(self):
        for i in self.incoming:
            i.initiate_close()
        for o in self.outgoing:
            o.initiate_close()

###############################################################################

class IncomingSocket(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()
        self.uuid = uuid.uuid4()
        self.ms = None

    def onConnecting(self, transport_details):
        logging.info("WebSocket connecting: %s" % transport_details)
        pass

    def onConnect(self, request):
        logging.info("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        logging.info("WebSocket connection open.")
        self.ms = MoneysocketSocket()
        self.ms._register_initiate_close_func(self.initiate_close)
        self.ms._register_initiate_send_func(self.initiate_send)
        self.factory.ms_interconnect._new_socket(self.ms)

    def onMessage(self, payload, isBinary):
        if isBinary:
            self.handle_binary(payload)
        else:
            self.handle_text(payload)

    def onClose(self, wasClean, code, reason):
        logging.info("WebSocket connection closed: {0}".format(reason))
        self.factory.ms_interconnect._socket_close(self.ms)
        self.ms = None

    ##########################################################################

    def initiate_close(self):
        super().sendClose()

    def initiate_send(self, msg_dict):
        s = self.sendMessage(json.dumps(msg_dict).encode("utf8"))
        logging.info("sent message, got: %s" % s)

    def handle_binary(self, payload):
        logging.info("binary payload: %d bytes" % len(payload))

    def handle_text(self, payload):
        logging.info("text payload: %s" % payload.decode("utf8"))
        self.ms._msg_recv(json.loads(payload.decode("utf8")))


class IncomingWebsocketInterconnect(MoneysocketInterconnect):
    def listen(self, bind, port, use_tls=None):
        if use_tls:
            contextFactory = ssl.DefaultOpenSSLContextFactory(
                use_tls['key_file'], use_tls['cert_file'],
                sslmethod=SSL.TLSv1_2_METHOD)
            factory = WebSocketServerFactory(u"wss://%s:%s" % (bind, port))
            factory.protocol = IncomingSocket
            factory.ms_interconnect = self
            listenWS(factory, contextFactory)
            print("listening tls")
        else:
            factory = WebSocketServerFactory(u"ws://%s:%s" % (bind, port))
            factory.protocol = IncomingSocket
            factory.ms_interconnect = self
            reactor.listenTCP(port, factory)
            print("listening clear")


###############################################################################

class OutgoingSocket(WebSocketClientProtocol):

    def onConnecting(self, transport_details):
        logging.info("WebSocket connecting: %s" % transport_details)

    def onConnect(self, response):
        logging.info("WebSocket connection connect: %s" % response)

    def onOpen(self):
        logging.info("WebSocket connection open.")
        self.ms = MoneysocketSocket()
        self.ms._register_initiate_close_func(self.initiate_close)
        self.ms._register_initiate_send_func(self.initiate_send)
        self.factory.ms_interconnect._new_socket(self.ms)
        pass

    def onMessage(self, payload, isBinary):
        if isBinary:
            self.handle_binary(payload)
        else:
            self.handle_text(payload)

    def onClose(self, wasClean, code, reason):
        logging.info("WebSocket connection closed: {0}".format(reason))
        self.factory.ms_interconnect._socket_close(self.ms)
        self.ms = None

    ##########################################################################

    def initiate_close(self):
        super().sendClose()

    def initiate_send(self, msg_dict):
        s = self.sendMessage(json.dumps(msg_dict).encode("utf8"))
        logging.info("sent message, got: %s" % s)

    def handle_binary(self, payload):
        logging.info("binary payload: %d bytes" % len(payload))

    def handle_text(self, payload):
        logging.info("text payload: %s" % payload.decode("utf8"))
        self.ms._msg_recv(json.loads(payload.decode("utf8")))

    ##########################################################################


class OutgoingWebsocketInterconnect(MoneysocketInterconnect):
    def connect(self, ws_url):
        logging.info("connect")
        factory = WebSocketClientFactory(ws_url)
        logging.info("factory: %s" % factory)
        factory.protocol = OutgoingSocket
        logging.info("factory 2 : %s" % factory)
        factory.ms_interconnect = self
        logging.info("factory 3h: %s" % factory)
        logging.info("connecting")
        c = connectWS(factory, timeout=10)
        logging.info("connect: %s" % c)
        # TODO - track pending connection attempts

    def connect_tls(self, ws_url):
        logging.info("connect: %s" % c)
        factory = WebSocketClientFactory(ws_url)
        factory.protocol = OutgoingSocket
        factory.ms_interconnect = self
        contextFactory = ssl.ClientContextFactory()
        connectWS(factory, contextFactory)

