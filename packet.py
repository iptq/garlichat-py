class BasePacket(object):
	def as_bytes(self):
		raise NotImplementedError("lol")

class DummyPacket(BasePacket):
	def as_bytes(self):
		return b"lol"