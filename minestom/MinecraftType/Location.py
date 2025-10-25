from dataclasses import dataclass
import struct

from minestom.PacketType import *


@dataclass
class Location:
    """位置基类，只包含基本坐标数据"""
    x: float
    y: float
    z: float
    dimension: str = "minecraft:world"

    def to_bytes(self):
        return encode_string(self.dimension) + struct.pack(">q", ((self.x & 0x3FFFFFF) << 38) | ((self.z & 0x3FFFFFF) << 12) | (self.y & 0xFFF))


@dataclass
class DeathLocation(Location):
    """死亡位置，继承自Location"""
    def __post_init__(self) -> bytes:
        """序列化为Minecraft数据包格式"""
        # 将坐标转换为整数方块坐标
        block_x, block_y, block_z = int(self.x), int(self.y), int(self.z)

        # 验证坐标范围
        if not (0 <= block_y < 4096):
            raise ValueError(f"Y coordinate {block_y} is out of range (0-4095)")
        if not (-33554432 <= block_x < 33554432):
            raise ValueError(f"X coordinate {block_x} is out of range (-33554432 to 33554431)")
        if not (-33554432 <= block_z < 33554432):
            raise ValueError(f"Z coordinate {block_z} is out of range (-33554432 to 33554431)")
        self.x = block_x
        self.y = block_y
        self.z = block_z

        # 编码位置为64位长整数
        # position_value = ((block_x & 0x3FFFFFF) << 38) | ((block_z & 0x3FFFFFF) << 12) | (block_y & 0xFFF)


@dataclass
class SpawnLocation(Location):
    """出生点位置，继承自Location"""
    angle: float = 0.0

    def to_bytes(self):
        return struct.pack(">q", ((self.x & 0x3FFFFFF) << 38) |
                           ((self.z & 0x3FFFFFF) << 12) |
                           (self.y & 0xFFF)) + struct.pack(">f", self.angle)


@dataclass
class PlayerPosition(Location):
    """玩家精确位置，继承自Location"""
    yaw: float = 0.0
    pitch: float = 0.0
    flags: int = 0
    teleport_id: int = 0
    dismount_vehicle: bool = False


@dataclass
class ChunkLocation:
    """区块位置，独立于Location"""
    chunk_x: int
    chunk_z: int
