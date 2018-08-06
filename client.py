import socket
import sys
from queue import Queue
from threading import Thread

import pysodium

from frontend import Application
from datagram import ClientHandshake, ServerHandshake, SecretBox
from packet import BasePacket, DummyPacket

class Garlichat(object):
    def __init__(self):
        self.to_server = Queue()
        self.to_client = Queue()

        self.gui = Application(self)
        self.ct = None
        self.sb = None

    def start_client(self):
        self.sock = socket.socket()
        self.sock.connect(("localhost", 23400))

        # handshake
        chs = ClientHandshake()
        self.sock.send(chs.as_bytes())

        # verify server handshake
        datagram = self.sock.recv(144)
        shs = ServerHandshake(chs.eph_pk, datagram)
        try:
            shs.verify()
        except Exception as e:
            traceback.print_exc()
            sys.exit(1)

        # harvest info from handshaeks
        print("Handshake phase complete.")
        rx_key, tx_key = pysodium.crypto_kx_server_session_keys(chs.eph_pk, chs.eph_sk, shs.eph_pk)
        self.sb = SecretBox(rx_key, tx_key)

        # send an update
        self.sock.send(self.sb.encrypt(DummyPacket()))

        while True:
            print("receiving...")
            sys.stdout.flush()
            data = self.sock.recv(1024)
            if not data: break
            print("len:", len(data))
            print(data)
            sys.stdout.flush()

    def start(self):
        # self.ft = Thread(target=self.gui.run)
        # self.ft.start()
        self.start_client()

    def quit(self):
        sys.exit(0)
