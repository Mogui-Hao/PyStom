import json
import struct
from dataclasses import field, dataclass
from uuid import UUID, uuid3

from nbtlib import Compound

from minestom.Minecraft import MinecraftConfig, GameMode
from minestom.MinecraftType import *
from minestom.Packet.PacketBase import ServerPacket
from minestom.PacketType import encode_string, encode_varint, encode_bytes, serialize_nbt


@dataclass
class ServerStatusResponsePacket(ServerPacket):
    config: MinecraftConfig = field(default_factory=MinecraftConfig())  # 服务器配置
    online: int = 0  # 在线人数
    sample: list = field(default_factory=list)  # 玩家样本

    @property
    def to_bytes(self) -> bytes:
        return json.dumps({"version": {"name": self.config.version, "protocol": self.config.versionProtocol},
                           "players": {"max": self.config.maxPlayers, "online": self.online, "sample": []},
                           "description": {"text": self.config.description},
                           "favicon": self.config.favicon}).encode("utf-8")

@dataclass
class ServerLoginSuccessPacket(ServerPacket):
    player_name: str  # 玩家名

    @property
    def to_bytes(self) -> bytes:
        return encode_bytes(uuid3(
                UUID('00000000-0000-0000-0000-000000000000'),
                f"OfflinePlayer:{self.player_name}").bytes) + encode_string(self.player_name)

@dataclass
class ServerSetCompressionPacket(ServerPacket):
    threshold: int  # 压缩值

    @property
    def to_bytes(self) -> int:
        return self.threshold

@dataclass
class ServerJoinGamePacket(ServerPacket):
    entity_id: int
    is_hardcore: bool = False
    game_mode: int = 1  # 0=生存, 1=创造, 2=冒险, 3=旁观
    previous_game_mode: int = -1  # -1表示未设置
    dimension_names: list[str] = field(default_factory=lambda: ["minecraft:overworld"])

    # 使用更简单的registry_codec进行测试
    registry_codec: dict = field(default_factory=lambda: {
        "minecraft:dimension_type": {
            "type": "minecraft:dimension_type",
            "value": [
                {
                    "name": "minecraft:overworld",
                    "id": 0,
                    "element": {
                        "min_y": 0,
                        "height": 256,
                        "logical_height": 256,
                        "natural": True,
                        "has_skylight": True,
                        "bed_works": True
                    }
                }
            ]
        }
    })

    dimension_type: str = "minecraft:overworld"
    dimension_name: str = "minecraft:overworld"
    hashed_seed: int = 0
    max_players: int = 0
    view_distance: int = 10
    simulation_distance: int = 10
    reduced_debug_info: bool = False
    enable_respawn_screen: bool = True
    is_debug: bool = False
    is_flat: bool = False
    death_location: DeathLocation | None = None
    portal_cooldown: int = 0

    @property
    def to_bytes(self) -> bytes:
        data = b""

        # 实体ID (int)
        data += struct.pack(">i", self.entity_id)

        # 硬核模式 (bool)
        data += bytes([1]) if self.is_hardcore else bytes([0])

        # 游戏模式 (unsigned byte)
        data += struct.pack(">B", self.game_mode)

        # 之前的游戏模式 (byte)
        data += struct.pack(">b", self.previous_game_mode)

        # 维度类型注册表名列表
        data += encode_varint(len(self.dimension_names))
        for name in self.dimension_names:
            data += encode_string(name)

        # 使用改进的NBT序列化器
        try:
            registry_bytes = serialize_nbt(self.registry_codec)
            # 保存NBT到文件用于调试
            with open("registry_codec.nbt", "wb") as f:
                f.write(registry_bytes)
            data += registry_bytes
        except Exception as e:
            print(f"NBT序列化错误: {e}")
            # 发送空NBT作为回退
            data += b'\x0a\x00\x00'  # 空Compound标签

        # 维度类型
        data += encode_string(self.dimension_type)

        # 维度名称
        data += encode_string(self.dimension_name)

        # 哈希种子 (long)
        data += struct.pack(">q", self.hashed_seed)

        # 最大玩家数 (已弃用，固定为0)
        data += encode_varint(self.max_players)  # 总是0

        # 视距 (VarInt)
        data += encode_varint(self.view_distance)

        # 模拟距离 (VarInt)
        data += encode_varint(self.simulation_distance)

        # 减少调试信息 (bool)
        data += bytes([1]) if self.reduced_debug_info else bytes([0])

        # 启用重生屏幕 (bool)
        data += bytes([1]) if self.enable_respawn_screen else bytes([0])

        # 调试模式 (bool)
        data += bytes([1]) if self.is_debug else bytes([0])

        # 超平坦世界 (bool)
        data += bytes([1]) if self.is_flat else bytes([0])

        # 死亡位置处理
        if self.death_location is not None:
            data += bytes([1])
            data += self.death_location.to_bytes()
        else:
            data += bytes([0])

        # 传送门冷却时间 (VarInt)
        data += encode_varint(self.portal_cooldown)

        # 保存完整数据包用于调试
        with open("joingame_packet.bin", "wb") as f:
            f.write(data)

        return data

@dataclass
class ServerSpawnPositionPacket(ServerPacket):
    location: SpawnLocation = field(default_factory=lambda: SpawnLocation(0, 0, 0))

    @property
    def to_bytes(self) -> bytes:
        return self.location.to_bytes()

@dataclass
class ServerPlayerPositionLookPacket(ServerPacket):
    """
    玩家位置和视角数据包 (0x38)
    用于设置玩家的位置、朝向和传送信息

    参数:
        x (float): X坐标
        y (float): Y坐标
        z (float): Z坐标
        yaw (float): 水平视角 (-180 到 180)
        pitch (float): 垂直视角 (-90 到 90)
        flags (int): 位置标志位 (0-7)，默认为0 (绝对位置)
        teleport_id (int): 传送ID，用于客户端确认
        dismount_vehicle (bool): 是否离开载具，默认为False
    """
    position: PlayerPosition = field(default_factory=lambda: PlayerPosition(0, 0, 0))

    @property
    def to_bytes(self) -> bytes:
        # 打包位置和视角数据
        data = struct.pack(">d", self.position.x)  # X坐标 (double)
        data += struct.pack(">d", self.position.y)  # Y坐标 (double)
        data += struct.pack(">d", self.position.z)  # Z坐标 (double)
        data += struct.pack(">f", self.position.yaw)  # 水平视角 (float)
        data += struct.pack(">f", self.position.pitch)  # 垂直视角 (float)

        # 位置标志位 (byte)
        # 每个位表示一个坐标/视角是否相对变化 (0=绝对，1=相对)
        # 位掩码:
        #   0x01: X坐标相对
        #   0x02: Y坐标相对
        #   0x04: Z坐标相对
        #   0x08: Yaw相对
        #   0x10: Pitch相对
        data += struct.pack(">B", self.position.flags)

        # 传送ID (VarInt)
        data += encode_varint(self.position.teleport_id)

        # 是否离开载具 (bool)
        data += struct.pack(">?", self.position.dismount_vehicle)

        return data

@dataclass
class ServerUpdateViewPositionPacket(ServerPacket):
    """
    更新视口位置数据包 (0x49)
    用于设置客户端视口的中心位置（区块坐标）

    参数:
        chunk_x (int): 视口中心的区块X坐标
        chunk_z (int): 视口中心的区块Z坐标
    """
    chunk: ChunkLocation = field(default_factory=lambda: ChunkLocation(0, 0))

    @property
    def to_bytes(self) -> bytes:
        """
        将数据包序列化为字节

        返回:
            bytes: 序列化后的数据包内容
        """
        # 构建数据包字节流
        data = b""

        # 添加区块X坐标 (VarInt)
        data += encode_varint(self.chunk.chunk_x)

        # 添加区块Z坐标 (VarInt)
        data += encode_varint(self.chunk.chunk_z)

        return data

@dataclass
class ServerChunkDataPacket(ServerPacket):
    """
    区块数据包 (0x22) - Minecraft 1.21.6
    用于向客户端发送区块数据
    """
    chunk_x: int
    chunk_z: int
    heightmaps: Compound = field(default_factory=Compound)
    chunk_data: bytes = b""
    block_entities: list[Compound] = field(default_factory=list)
    trust_edges: bool = True
    sky_light_mask: list[int] = field(default_factory=list)
    block_light_mask: list[int] = field(default_factory=list)
    empty_sky_light_mask: list[int] = field(default_factory=list)
    empty_block_light_mask: list[int] = field(default_factory=list)
    light_arrays: list[bytes] = field(default_factory=list)

    @property
    def to_bytes(self) -> bytes:
        data = b""

        # 区块坐标 (int)
        data += struct.pack(">i", self.chunk_x)
        data += struct.pack(">i", self.chunk_z)

        # 高度图 (NBT)
        heightmaps_bytes = serialize_nbt(self.heightmaps)
        if isinstance(heightmaps_bytes, str):
            heightmaps_bytes = heightmaps_bytes.encode('utf-8')
        data += encode_varint(len(heightmaps_bytes))
        data += heightmaps_bytes

        # 区块数据 (字节数组)
        data += encode_varint(len(self.chunk_data))
        data += self.chunk_data

        # 方块实体 (NBT列表)
        data += encode_varint(len(self.block_entities))
        for entity in self.block_entities:
            entity_bytes = serialize_nbt(entity)
            if isinstance(entity_bytes, str):
                entity_bytes = entity_bytes.encode('utf-8')
            data += entity_bytes

        # 信任边缘 (bool)
        data += b"\x01" if self.trust_edges else b"\x00"

        # 光照掩码处理
        data += self._encode_bitset(self.sky_light_mask)
        data += self._encode_bitset(self.block_light_mask)
        data += self._encode_bitset(self.empty_sky_light_mask)
        data += self._encode_bitset(self.empty_block_light_mask)

        # 光照数据数组
        data += encode_varint(len(self.light_arrays))
        for light_array in self.light_arrays:
            data += encode_varint(len(light_array))
            data += light_array

        return data

    def _encode_bitset(self, bitset: list[int]) -> bytes:
        """编码BitSet为字节"""
        data = encode_varint(len(bitset))
        for value in bitset:
            data += struct.pack(">q", value)
        return data

@dataclass
class ServerPlayerAbilitiesPacket(ServerPacket):
    """
    玩家能力数据包 (0x32)

    参数:
        flags (int): 能力标志 (位掩码)
            0b0001 0x01: 无敌
            0b0010 0x02: 飞行
            0b0100 0x04: 允许飞行
            0b1000 0x08: 创造模式
        flying_speed (float): 飞行速度 (默认0.05)
        field_of_view_modifier (float): 视野修改器 (默认0.1)
    """
    flags: int
    flying_speed: float = 0.05
    field_of_view_modifier: float = 0.1

    @property
    def to_bytes(self) -> bytes:
        # 确保flags在0-255范围内
        if not 0 <= self.flags <= 255:
            raise ValueError("Flags must be between 0 and 255")

        return (
                struct.pack(">B", self.flags) +
                struct.pack(">f", self.flying_speed) +
                struct.pack(">f", self.field_of_view_modifier)
        )

@dataclass
class ServerPlayerInfoPacket(ServerPacket):
    """
    玩家信息数据包 (0x36) - 用于添加/更新玩家列表
    """
    action: int  # 0=添加玩家, 1=更新游戏模式, 2=更新延迟, 3=更新显示名, 4=移除玩家
    uuid: UUID  # 玩家UUID
    name: str  # 玩家名
    properties: list  # 玩家属性列表
    gamemode: int  # 游戏模式 (0-3)
    ping: int  # 延迟(ms)
    has_display_name: bool = False  # 是否有显示名称
    display_name: str | None = None  # 显示名称(JSON文本)

    @property
    def to_bytes(self) -> bytes:
        data = b""

        # 动作类型 (VarInt)
        data += encode_varint(self.action)

        # 玩家数量 (此处固定为1)
        data += encode_varint(1)

        # 玩家UUID
        data += self.uuid.bytes

        # 玩家名
        data += encode_string(self.name)

        # 属性列表
        data += encode_varint(len(self.properties))
        for prop in self.properties:
            # 属性结构实现需根据实际需求
            pass

        # 游戏模式 (VarInt)
        data += encode_varint(self.gamemode)

        # 延迟 (VarInt)
        data += encode_varint(self.ping)

        # 是否有显示名称
        data += bytes([1]) if self.has_display_name else bytes([0])

        # 显示名称 (如果存在)
        if self.has_display_name and self.display_name:
            data += encode_string(self.display_name)

        return data

@dataclass
class ServerUpdateHealthPacket(ServerPacket):
    """
    更新生命值数据包 (0x52)
    """
    health: float  # 生命值 (0.0-20.0)
    food: int  # 饥饿值 (0-20)
    food_saturation: float  # 饱和度

    @property
    def to_bytes(self) -> bytes:
        return (
            struct.pack(">f", self.health) +
            encode_varint(self.food) +
            struct.pack(">f", self.food_saturation)
        )

@dataclass
class ServerPluginMessagePacket(ServerPacket):
    """
    插件消息数据包 (0x19) - 用于发送自定义数据
    """
    channel: str  # 频道标识符
    data: bytes  # 自定义数据

    @property
    def to_bytes(self) -> bytes:
        return encode_string(self.channel) + self.data


@dataclass
class ServerTimeUpdatePacket(ServerPacket):
    """
    时间更新数据包 (0x5E) - 用于同步世界时间
    参数:
        world_age (long): 世界总存在时间 (单位: 游戏刻)
        time_of_day (long): 当天时间 (0-24000, 0=黎明, 6000=正午, 12000=日落, 18000=午夜)
    """
    world_age: int
    time_of_day: int

    @property
    def to_bytes(self) -> bytes:
        """
        将数据包序列化为字节

        返回:
            bytes: 序列化后的数据包内容
        """
        # 使用大端序打包两个长整数
        return struct.pack(">q", self.world_age) + struct.pack(">q", self.time_of_day)


@dataclass
class ServerKeepAlivePacket(ServerPacket):
    """
    心跳包 (0x23) - 用于保持客户端连接
    参数:
        keep_alive_id (long): 心跳包唯一ID
    """
    keep_alive_id: int

    @property
    def to_bytes(self) -> bytes:
        """
        将数据包序列化为字节

        返回:
            bytes: 序列化后的数据包内容
        """
        # 使用大端序打包长整数
        return struct.pack(">q", self.keep_alive_id)
