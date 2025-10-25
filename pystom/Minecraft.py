
from dataclasses import dataclass
from enum import Enum, unique


@dataclass
class MinecraftConfig:
    version: str = "Python 3.13 - 1.21.x"
    versionProtocol: int = 771
    maxPlayers: int = 20
    description: str = "A Python Minecraft Server"
    favicon: str = ""

@unique
class MinecraftStatus(Enum):
    HANDSHAKING = 0
    STATUS = 1
    LOGIN = 2
    PLAY = 3

@unique
class GameMode(Enum):
    SURVIVAL = 0  # 生存模式
    CREATIVE = 1  # 创造模式
    ADVENTURE = 2  # 冒险模式
    SPECTATOR = 3  # 旁观模式
