# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import logging
import uuid

from OpenSSL import SSL

from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import listenWS
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.websocket import WebSocketServerProtocol

from autobahn.twisted.websocket import connectWS
from autobahn.twisted.websocket import WebSocketClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol

from moneysocket.socket.socket import MoneysocketSocket, MoneysocketTransport



class WebsocketTransport(MoneysocketTransport):
    def __init__(self, incoming=True, outgoing=True):
        super().__init__()
        self.incoming = incoming
        self.outgoing = outgoing


    def listen(self, bind, port, use_tls=None):
        pass

###############################################################################

class IncomingSocket(WebSocketServerProtocol):

    def onConnecting(self, transport_details):
        logging.info("WebSocket connecting: %s" % transport_details)
        pass

    def onConnect(self, request):
        self.uuid = uuid.uuid4()
        self.ms_transport = self.factory.ms_transport

        print(self.factory)
        logging.info("Client connecting: {0}".format(request.peer))

        self.ms_transport.connect(self, request)

    def onOpen(self):
        logging.info("WebSocket connection open.")
        self.ms_transport.open(self.uuid)

    def onMessage(self, payload, isBinary):
        if isBinary:
            logging.info(
                "Binary message received: {0} bytes".format( len(payload)))
            logging.info("Binary message received: %s" % payload.hex())
        else:
            decoded = payload.decode('utf8')
            logging.info(
                "Text message received: {0}".format(decoded))

    def onClose(self, wasClean, code, reason):
        logging.info("WebSocket connection closed: {0}".format(reason))

    ##########################################################################

    def close(self):
        self.close()

    def send(self, msg_dict):
        self.sendMessage(json.dumps(msg_dict).encode("utf8"))

    def handle_binary(self, payload):
        logging.info("binary payload: %d bytes" % len(payload))

    def handle_text(self, payload):
        logging.info("text payload: %s" % payload.decode("utf8"))
        self.ms.recv_msg(json.loads(payload.decode("utf8")))



class IncomingWebsocketTransport(WebsocketTransport):
    def __init__(self, bind, port, use_tls=None):
        super().__init__()

        self.connections = {}
        if use_tls:
            contextFactory = ssl.DefaultOpenSSLContextFactory(
                use_tls['key_file'], use_tls['cert_file'],
                sslmethod=SSL.TLSv1_2_METHOD)
            factory = WebSocketServerFactory(u"wss://%s:%s" % (bind, port))
            factory.protocol = IncomingSocket
            factory.ms_transport = self
            listenWS(factory, contextFactory)
            print("listening tls")
        else:
            factory = WebSocketServerFactory(u"ws://%s:%s" % (bind, port))
            factory.protocol = IncomingSocket
            factory.ms_transport = self
            reactor.listenTCP(port, factory)
            print("listening clear")

    def connect(self, connection, request):
        self.connections[connection.uuid] = connection

    def open(self, uuid):
        pass

    def message(self, uuid, payload, isBinary):
        pass

    def close(self, uuid, wasClean, code, reason):
        if uuid in self.connections.keys():
            del self.connections[uuid]


###############################################################################

class OutgoingSocket(WebSocketClientProtocol):

    def onConnecting(self, transport_details):
        logging.info("WebSocket connecting: %s" % transport_details)
        pass

    def onConnect(self, response):
        logging.info("WebSocket connection connect: %s" % response)

    def onOpen(self):
        logging.info("WebSocket connection open.")
        self.ms = MoneysocketSocket()
        self.ms.set_close_func(self.close)
        self.factory.transport.socket_spawn(self.ms)
        pass

    def onMessage(self, payload, isBinary):
        if isBinary:
            self.handle_binary(payload)
        else:
            self.handle_text(payload)

    def onClose(self, wasClean, code, reason):
        logging.info("WebSocket connection closed: {0}".format(reason))
        self.ms = None

    ##########################################################################

    def close(self):
        self.close()

    def send(self, msg_dict):
        self.sendMessage(json.dumps(msg_dict).encode("utf8"))

    def handle_binary(self, payload):
        logging.info("binary payload: %d bytes" % len(payload))

    def handle_text(self, payload):
        logging.info("text payload: %s" % payload.decode("utf8"))
        self.ms.recv_msg(json.loads(payload.decode("utf8")))

    ##########################################################################


class OutgoingWebsocketTransport(MoneysocketTransport):
    def __init__(self):
        super().__init__()


    def connect(self, ws_url):
        factory = WebSocketClientFactory(ws_url)
        factory.protocol = OutgoingSocket
        factory.transport = self
        connectWS(factory)

    def connect_tls(self, ws_url):
        factory = WebSocketClientFactory(ws_url)
        factory.protocol = OutgoingSocket
        factory.transport = self
        contextFactory = ssl.ClientContextFactory()
        connectWS(factory, contextFactory)

