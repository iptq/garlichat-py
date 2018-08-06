import ctypes
import secrets
import struct

import pysodium

# lol
def check(code):
    if code != 0:
        raise ValueError

class ClientHandshake(object):
	def __init__(self):
		self.eph_pk = None
		self.eph_sk = None
		self.sign_pk = None
		self.sign_sk = None

	def as_bytes(self):
		# magic signature
		datagram = bytearray("GARLICKYCLIENT", "ascii")
		# protocol version number
		datagram.extend(struct.pack("<H", 0))

		# generate ephemeral key
		self.eph_pk, self.eph_sk = pysodium.crypto_kx_keypair()
		assert len(self.eph_pk) == 32
		datagram.extend(self.eph_pk)

		# generate keypair for signature
		self.sign_pk, self.sign_sk = pysodium.crypto_sign_keypair()
		assert len(self.sign_pk) == 32
		datagram.extend(self.sign_pk)

		# sign the ephemeral key cus untrusted apparently :/
		# print(pysodium.sodium.crypto_sign_ed25519_detached)
		sig = ctypes.create_string_buffer(pysodium.crypto_sign_BYTES)
		check(pysodium.sodium.crypto_sign_ed25519_detached(
			sig,
			ctypes.c_void_p(0),
			self.eph_pk,
			ctypes.c_ulonglong(len(self.eph_pk)),
			self.sign_sk,
		))
		assert len(sig) == 64
		# pysodium.crypto_sign_detached(eph_pk, sign_sk)
		datagram.extend(sig)

		assert len(datagram) == 144
		return datagram

class ServerHandshake(object):
	def __init__(self, cpk, datagram):
		self.cpk = cpk # client's ephemeral public key
		self.datagram = datagram
		self.eph_pk = None
		self.sign_pk = None

	def verify(self):
		# magic header
		magic = b"GARLICKYSERVER"
		assert self.datagram[:len(magic)] == magic

		# protocol version
		ver, = struct.unpack("<H", self.datagram[len(magic):len(magic)+2])
		assert ver == 0

		# get keys=
		self.eph_pk = self.datagram[16:48]
		self.sign_pk = self.datagram[48:80]
		sig = self.datagram[80:144]

		m = bytearray(self.cpk)
		m.extend(self.eph_pk)
		if pysodium.sodium.crypto_sign_ed25519_verify_detached(
			sig,
			bytes(m),
			ctypes.c_ulonglong(len(m)),
			self.sign_pk,
		) != 0:
			raise ValueError("verification of server's ephemeral public key failed.")
		return True

class SecretBox(object):
	def __init__(self, rx_key, tx_key):
		self.rx_key = rx_key
		self.tx_key = tx_key

	def decrypt(self, datagram):
		len = struct.unpack("<Q", datagram[:8])
		nonce = datagram[8:32]
		enc = datagram[32:32+len]
		# decrypt

	def encrypt(self, packet):
		datagram = bytearray()
		data = packet.as_bytes()
		nonce = secrets.token_bytes(24)
		datagram.extend(struct.pack("<Q", len(data)))
		datagram.extend(nonce)
