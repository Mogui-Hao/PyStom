import struct
from nbtlib import Compound, String, Long, List
from pystom.PacketType import encode_varint


def create_simple_chunk_data(chunk_x: int, chunk_z: int, biome_id: int = 0) -> bytes:
    """创建符合 1.21.6 协议的简化区块数据"""
    # 1. 区块章节数量 (24 个章节，覆盖 -64 到 320)
    section_count = 24
    chunk_data = encode_varint(section_count)

    # 2. 每个章节的数据
    for _ in range(section_count):
        # 2.1 方块数量 (全空气)
        chunk_data += struct.pack(">h", 0)  # 非空气方块数量为0

        # 2.2 方块状态数据
        # - 调色板大小 (1: 只有空气)
        chunk_data += encode_varint(1)
        # - 调色板内容 (空气方块ID)
        chunk_data += encode_varint(0)  # 空气方块ID
        # - 数据数组长度 (0: 不需要数据数组)
        chunk_data += encode_varint(0)

        # 2.3 生物群系数据 (使用VarInt编码)
        biome_data = b""
        for _ in range(64):  # 4x4x4 生物群系网格
            biome_data += encode_varint(biome_id)  # 使用VarInt编码

        chunk_data += encode_varint(len(biome_data))
        chunk_data += biome_data

        # 2.4 光照数据 (1.21.6 要求)
        # - 天空光照掩码 (空)
        chunk_data += encode_varint(0)  # 空BitSet
        # - 方块光照掩码 (空)
        chunk_data += encode_varint(0)  # 空BitSet
        # - 空天空光照掩码 (全章节)
        chunk_data += encode_varint(0xFFFFFFFF)  # 所有章节都需要天空光照
        # - 空方块光照掩码 (全章节)
        chunk_data += encode_varint(0xFFFFFFFF)  # 所有章节都需要方块光照
        # - 光照数据数组 (空)
        chunk_data += encode_varint(0)  # 无光照数据

    # 3. 区块实体数据 (空)
    chunk_data += encode_varint(0)  # 无区块实体

    # 4. 信任边缘 (False)
    chunk_data += b'\x00'

    # 5. 光照数据结束标记
    chunk_data += encode_varint(0)  # 天空光照更新部分为空
    chunk_data += encode_varint(0)  # 方块光照更新部分为空

    return chunk_data


def create_simple_heightmap() -> Compound:
    """创建符合 1.21.6 协议的高度图"""
    # 创建高度图数据 (所有位置高度为 64)
    height_data = []
    for _ in range(37):  # 16x16 区块需要 37 个长整数 (256/7≈36.57)
        value = 0
        for bit in range(7):
            value |= (64 << (bit * 9))
        height_data.append(Long(value))

    return Compound({
        "MOTION_BLOCKING": Compound({
            "type": String("LONG_ARRAY"),
            "value": List(height_data)
        }),
        "WORLD_SURFACE": Compound({
            "type": String("LONG_ARRAY"),
            "value": List(height_data)
        })
    })
