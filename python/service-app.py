#!/usr/bin/env python3

import logging
import argparse

from twisted.internet import reactor

from twisted.conch.telnet import TelnetTransport, TelnetProtocol
from twisted.internet.protocol import ServerFactory
from twisted.application.internet import TCPServer
from twisted.application.service import Application

from moneysocket.socket.websocket import WebsocketInterconnect



class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.send_usage = False
        self.send_message = None

    def error(self, message):
        print(message)
        self.send_usage = True
        self.send_message = message



class AppTelnetInterface(TelnetProtocol):
    APP = None

    def __init__(self):
        super().__init__()


    def prep_parser(self):
        parser = ArgumentParser()

        subparsers = parser.add_subparsers(dest="subparser_name",
                                           title='commands',
                                           description='valid app commands',
                                           help='app commands')

        parser_ls = subparsers.add_parser('ls', help='list summary')
        parser_ls.set_defaults(cmd=self.APP.ls)

        parser_new_service = subparsers.add_parser("newservice")
        parser_new_service.set_defaults(cmd=self.APP.newservice)

        parser_new_wallet = subparsers.add_parser("newwallet")
        parser_new_wallet.set_defaults(cmd=self.APP.newwallet)

        parser_connect = subparsers.add_parser('connect',
                                               help='connect to websocket')
        parser_connect.set_defaults(cmd=self.APP.connect)

        parser_listen = subparsers.add_parser('listen',
                                              help='listen to websocket')
        parser_connect.set_defaults(cmd=self.APP.listen)

        return parser

    def parse(self, args):
        print(args)
        parser = self.prep_parser()
        if not args or len(args) == 0:
            self.transport.write((parser.format_usage() + "\n").encode("utf8"))
            return None

        try:
            parsed = parser.parse_args(args)
        except Exception:
            pass

        if parser.send_usage:
            msg = parser.send_message
            self.transport.write((msg + "\n").encode("utf8"))
            return None
        if not parsed.subparser_name:
            self.transport.write((parser.format_usage() + "\n").encode("utf8"))
            return None

        return parsed


    def dataReceived(self, data):
        args = data.decode("utf8").rstrip().split(" ")
        args = [a for a in args if a != ""]
        print("args: %s" % args)
        args = self.parse(args)
        if not args:
            self.transport.write(b"moneysocket> ")
            return

        cmd_response = args.cmd(args)

        self.transport.write((cmd_response + "\n").encode("utf8"))
        print(args)
        self.transport.write(b"moneysocket> ")



class ServiceApp(object):
    def __init__(self):
        self.services = []
        self.wallets = []

    def ls(self, args):
        return "ls"

    def connect(self, args):
        return "connect"

    def listen(self, args):
        return "listen"

    def newservice(self, args):
        return "newservice"

    def newwallet(self, args):
        return "newwallet"


app = ServiceApp()
AppTelnetInterface.APP = app


logging.basicConfig(level=logging.DEBUG)

#wi = WebsocketInterconnect(new_socket_cb, socket_close_cb)
#wi.connect("ws://localhost:9999")




TELNET_CMD_PORT = 9999
factory = ServerFactory()
factory.protocol = lambda: TelnetTransport(AppTelnetInterface)
service = TCPServer(TELNET_CMD_PORT, factory)
service.startService()

#application = Application("Telnet Echo Server")
#service.setServiceParent(application)

#print("running reactor")
reactor.run()
