import struct
from io import BytesIO

type VarInt = bytes

def encode_varint(value: int) -> VarInt:
    _bytes = []
    while ...:
        byte = value & 127
        value >>= 7
        if value:
            byte |= 128
        _bytes.append(byte)
        if not value:
            break
    return bytes(_bytes)

def decode_varint(_bytes: bytes, index: int = 0) -> int:
    # 分割字节列表为各个VarInt的字节数组
    varint_list = []
    current = []
    for b in list(_bytes):
        current.append(b)
        if (b & 0x80) == 0:  # 检查最高位是否为0
            varint_list.append(current)
            current = []
    # 检查索引是否有效
    if index >= len(varint_list):
        raise IndexError("VarInt index out of range")
    value = 0
    offset = 0
    for b in varint_list[index]:
        value |= (b & 0x7F) << (offset * 7)
        offset += 1
    return value

def varint_length(_bytes: bytes, index: int = 0) -> int:
    length = 0
    for b in _bytes[index:]:
        length += 1
        if (b & 0x80) == 0:
            return length
    raise ValueError("VarInt未完整")

def encode_string(data: str) -> bytes:
    return encode_varint(len(data.encode("utf-8"))) + data.encode("utf-8")

def encode_bytes(data: bytes) -> bytes:
    return encode_varint(len(data)) + data


# 改进的NBT序列化器 - 修复所有已知问题
def serialize_nbt(tag):
    """序列化NBT标签为Minecraft协议兼容的二进制格式"""
    buffer = BytesIO()
    _serialize_tag(tag, buffer, with_name=False)  # 根标签没有名称
    return buffer.getvalue()


def _serialize_tag(tag, buffer, with_name=True):
    """递归序列化NBT标签"""
    if isinstance(tag, dict):
        # Compound标签
        buffer.write(b'\x0a')  # Compound类型ID (10)
        if with_name:
            _write_name("", buffer)  # 根标签没有名称

        for key, value in tag.items():
            # 写入键名
            key_bytes = key.encode('utf-8')
            buffer.write(struct.pack('>H', len(key_bytes)))
            buffer.write(key_bytes)

            # 递归写入值
            _serialize_tag(value, buffer, with_name=False)

        buffer.write(b'\x00')  # 结束标签 (TAG_End)

    elif isinstance(tag, list):
        # List标签 - 这是最复杂的部分
        if not tag:
            # 空列表
            buffer.write(b'\x09')  # List类型ID (9)
            if with_name:
                _write_name("", buffer)
            buffer.write(b'\x00')  # 元素类型 (TAG_End)
            buffer.write(struct.pack('>i', 0))  # 元素数量
            return

        # 确定列表中所有元素的类型
        first_type = _get_nbt_type(tag[0])
        for item in tag:
            if _get_nbt_type(item) != first_type:
                raise ValueError("列表中的所有元素必须是相同类型")

        buffer.write(b'\x09')  # List类型ID (9)
        if with_name:
            _write_name("", buffer)

        buffer.write(struct.pack('>B', first_type))  # 元素类型
        buffer.write(struct.pack('>i', len(tag)))  # 元素数量

        for item in tag:
            _serialize_tag(item, buffer, with_name=False)  # 列表元素没有名称

    elif isinstance(tag, str):
        # String标签
        buffer.write(b'\x08')  # String类型ID (8)
        if with_name:
            _write_name("", buffer)

        str_bytes = tag.encode('utf-8')
        buffer.write(struct.pack('>H', len(str_bytes)))
        buffer.write(str_bytes)

    elif isinstance(tag, int):
        # Int标签
        buffer.write(b'\x03')  # Int类型ID (3)
        if with_name:
            _write_name("", buffer)
        buffer.write(struct.pack('>i', tag))

    elif isinstance(tag, float):
        # Float标签
        buffer.write(b'\x05')  # Float类型ID (5)
        if with_name:
            _write_name("", buffer)
        buffer.write(struct.pack('>f', tag))

    elif tag is True or tag is False:
        # Byte标签（用于布尔值）
        buffer.write(b'\x01')  # Byte类型ID (1)
        if with_name:
            _write_name("", buffer)
        buffer.write(bytes([1] if tag else [0]))

    else:
        raise ValueError(f"不支持的NBT类型: {type(tag)}")


def _get_nbt_type(value):
    """获取NBT类型ID"""
    if isinstance(value, dict):
        return 10  # Compound
    elif isinstance(value, list):
        return 9  # List
    elif isinstance(value, str):
        return 8  # String
    elif isinstance(value, int):
        return 3  # Int
    elif isinstance(value, float):
        return 5  # Float
    elif isinstance(value, bool):
        return 1  # Byte
    else:
        raise ValueError(f"不支持的NBT类型: {type(value)}")


def _write_name(name, buffer):
    """写入标签名称（长度前缀的UTF-8字符串）"""
    name_bytes = name.encode('utf-8')
    buffer.write(struct.pack('>H', len(name_bytes)))
    buffer.write(name_bytes)