
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Packet(ABC):
    @property
    @abstractmethod
    def to_bytes(self) -> bytes: ...

    @classmethod
    @abstractmethod
    def parser(cls, data: bytes): ...

@dataclass
class ClientPacket(Packet):
    @classmethod
    @abstractmethod
    def parser(cls, data: bytes): ...

    def to_bytes(self) -> bytes: return b''

@dataclass
class ServerPacket(Packet):
    def parser(self, data: bytes): return self

    @property
    @abstractmethod
    def to_bytes(self) -> bytes: ...
