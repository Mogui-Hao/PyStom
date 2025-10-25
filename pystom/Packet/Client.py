import struct
from dataclasses import dataclass

from pystom.Minecraft import MinecraftStatus
from pystom.Packet.PacketBase import ClientPacket
from pystom.PacketType import decode_varint, varint_length


@dataclass
class ClientHandshakingPacket(ClientPacket):
    versionProtocol: int
    ip: str
    port: int
    status: MinecraftStatus

    @classmethod
    def parser(cls, data: bytes):
        ptr = varint_length(data, 0)
        protocol = decode_varint(data, ptr)
        ptr += varint_length(data, ptr)
        length = data[ptr]
        ptr += varint_length(data, ptr)
        ip = data[ptr:ptr + length].decode("utf-8")
        ptr += length
        port = int.from_bytes(data[ptr:ptr + 2], byteorder='big')
        ptr += 2
        return ClientHandshakingPacket(protocol, ip, port, MinecraftStatus(data[ptr]))

@dataclass
class ClientStatusRequestPacket(ClientPacket):
    @classmethod
    def parser(cls, data: bytes) -> 'ClientStatusRequestPacket': return ClientStatusRequestPacket()

@dataclass
class ClientStatusPingPacket(ClientPacket):
    byte: bytes
    @classmethod
    def parser(cls, data: bytes) -> 'ClientStatusPingPacket':
        return ClientStatusPingPacket(data)

@dataclass
class ClientLoginRequest(ClientPacket):
    player_name: str

    @classmethod
    def parser(cls, data: bytes) -> 'ClientLoginRequest':
        ptr = varint_length(data, 0)
        length = decode_varint(data, ptr)
        ptr += varint_length(data, 1)
        return ClientLoginRequest(data[ptr:ptr + length].decode("utf-8"))

@dataclass
class ClientKeepAlivePacket(ClientPacket):
    keep_alive_id: int

    @classmethod
    def parser(cls, data: bytes) -> 'ClientKeepAlivePacket':
        # 长整型 (8字节)
        keep_alive_id = int.from_bytes(data[:8], byteorder='big', signed=True)
        return ClientKeepAlivePacket(keep_alive_id)

@dataclass
class ClientPlayerPositionPacket(ClientPacket):
    x: float
    feet_y: float
    z: float
    on_ground: bool

    @classmethod
    def parser(cls, data: bytes) -> 'ClientPlayerPositionPacket':
        # 三个双精度浮点数 (各8字节) + 一个布尔值 (1字节)
        x, feet_y, z = struct.unpack('>ddd', data[:24])
        on_ground = bool(data[24])
        return ClientPlayerPositionPacket(x, feet_y, z, on_ground)

@dataclass
class ClientPlayerPositionLookPacket(ClientPacket):
    x: float
    feet_y: float
    z: float
    yaw: float
    pitch: float
    on_ground: bool

    @classmethod
    def parser(cls, data: bytes) -> 'ClientPlayerPositionLookPacket':
        # 三个双精度浮点数 (各8字节) + 两个单精度浮点数 (各4字节) + 一个布尔值 (1字节)
        x, feet_y, z = struct.unpack('>ddd', data[:24])
        yaw, pitch = struct.unpack('>ff', data[24:32])
        on_ground = bool(data[32])
        return ClientPlayerPositionLookPacket(x, feet_y, z, yaw, pitch, on_ground)

@dataclass
class ClientPlayerLookPacket(ClientPacket):
    yaw: float
    pitch: float
    on_ground: bool

    @classmethod
    def parser(cls, data: bytes) -> 'ClientPlayerLookPacket':
        # 两个单精度浮点数 (各4字节) + 一个布尔值 (1字节)
        yaw, pitch = struct.unpack('>ff', data[:8])
        on_ground = bool(data[8])
        return ClientPlayerLookPacket(yaw, pitch, on_ground)

@dataclass
class ClientTeleportConfirmPacket(ClientPacket):
    teleport_id: int

    @classmethod
    def parser(cls, data: bytes) -> 'ClientTeleportConfirmPacket':
        # 变长整数 (VarInt)
        ptr = 0
        teleport_id, length = decode_varint(data, ptr)
        return ClientTeleportConfirmPacket(teleport_id)

@dataclass
class ClientSettingsPacket(ClientPacket):
    locale: str
    view_distance: int
    chat_mode: int
    chat_colors: bool
    skin_parts: int
    main_hand: int
    disable_text_filtering: bool  # 1.21.6新增

    @classmethod
    def parser(cls, data: bytes) -> 'ClientSettingsPacket':
        ptr = 0

        # 解析locale (字符串)
        length = data[ptr]
        ptr += varint_length(data, ptr)
        locale = data[ptr:ptr + length].decode("utf-8")

        # 视距 (字节)
        view_distance = data[ptr]
        ptr += 1

        # 聊天模式 (VarInt)
        chat_mode, length = decode_varint(data, ptr)
        ptr += length

        # 聊天颜色 (布尔)
        chat_colors = bool(data[ptr])
        ptr += 1

        # 皮肤显示设置 (字节)
        skin_parts = data[ptr]
        ptr += 1

        # 主手设置 (VarInt)
        main_hand, length = decode_varint(data, ptr)
        ptr += length

        # 禁用文本过滤 (1.21.6新增)
        disable_text_filtering = bool(data[ptr])

        return ClientSettingsPacket(
            locale,
            view_distance,
            chat_mode,
            chat_colors,
            skin_parts,
            main_hand,
            disable_text_filtering
        )
