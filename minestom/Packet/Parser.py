from minestom.Minecraft import MinecraftStatus
# from minestom.Packet.Client import (ClientHandshakingPacket, ClientStatusRequestPacket, ClientStatusPingPacket,
#                                     ClientLoginRequest)
from minestom.Packet.Client import *
from minestom.PacketType import varint_length, decode_varint


def parser_packet(data: bytes, status: MinecraftStatus):
    match status:
        case MinecraftStatus.HANDSHAKING:
            match decode_varint(data, 0):
                case 0x00:
                    return ClientHandshakingPacket.parser(data)
        case MinecraftStatus.STATUS:
            match decode_varint(data, 0):
                case 0x00:
                    return ClientStatusRequestPacket.parser(data)
                case 0x01:
                    return ClientStatusPingPacket.parser(data)
        case MinecraftStatus.LOGIN:
            match decode_varint(data, 0):
                case 0x00:
                    return ClientLoginRequest.parser(data)
        case MinecraftStatus.PLAY:
            match decode_varint(data, 0):
                case 0x10:
                    return ClientKeepAlivePacket.parser(data)
                case 0x13:
                    return ClientPlayerPositionPacket.parser(data)
                case 0x14:
                    return ClientPlayerPositionLookPacket.parser(data)
                case 0x15:
                    return ClientPlayerLookPacket.parser(data)
                case 0x00:
                    return ClientTeleportConfirmPacket.parser(data)
                case 0x08:
                    return ClientSettingsPacket.parser(data)
