# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import logging


class MoneysocketSocket(object):
    def __init__(self):
        self.msg_recv_cb = None
        self.close_func = None
        pass

    def register_msg_recv_cb(self, cb):
        self.msg_recv_cb = cb

    def set_close_func(self, close_func):
        self.close_func = close_func

    def recv_msg(self, msg_dict):
        if not self.msg_recv_cb:
            logging.error("no spawn callback registered!")
            return
        self.msg_recv_cb(msg_dict)

    def send_msg(self, msg_dict):
        pass

    def close(self):
        self.close_func()
        pass



class MoneysocketTransport(object):
    def __init__(self):
        self.spawn_cb = None
        self.close_cb = None

    def register_socket_spawn_cb(self, cb):
        self.spawn_cb = cb

    def register_socket_close_cb(self, cb):
        self.close_cb = cb

    def socket_spawn(self, moneysocket_socket):
        if not self.spawn_cb:
            logging.error("no spawn callback registered!")
            return
        self.spawn_cb(moneysocket_socket)

    def socket_closed(self, moneysocket_socket):
        if not self.close_cb:
            logging.error("no close callback registered!")
            return
        self.close_cb(moneysocket_socket)

