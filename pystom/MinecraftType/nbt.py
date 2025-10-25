import struct
from enum import Enum, unique
from typing import Tuple
import gzip


def IdToNbt(tag_id: int) -> 'NBTObject':
    match tag_id:
        case 0x00:
            return End
        case 0x01:
            return Byte
        case 0x02:
            return Short
        case 0x03:
            return Int
        case 0x04:
            return Long
        case 0x05:
            return Float
        case 0x06:
            return Double
        case 0x07:
            return ByteArray
        case 0x08:
            return String
        case 0x09:
            return List
        case 0x0A:
            return Compound
        case 0x0B:
            return IntArray
        case 0x0C:
            return LongArray
        case a:
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", a)


class NBTObject(object):
    """NBT类型对象"""
    TAG_ID = None

    def __init__(self, name: str, value):
        self._value = None
        self._name = ""

    def serialize(self) -> bytearray:
        """序列化"""

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        """从值序列化"""

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        """反序列化"""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, (str, bytearray, bytes)): raise TypeError("name must be string or bytes")
        self._name = value

    def __repr__(self):
        return f"{self.__class__.__name__}(name=\"{self.name}\", value={self.value})" if self.name != "" else f"{self.__class__.__name__}({self.value})"

    __str__ = __repr__


class End(NBTObject):
    TAG_ID = 0x00

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        if data != bytes([cls.TAG_ID]):
            raise ValueError
        if return_offset:
            return cls(), 1
        return cls()


class Byte(NBTObject):
    """表示NBT的Byte类型"""
    TAG_ID = 0x01

    def __init__(self, name: str = "", value: int = 0):
        super().__init__(name, value)
        self.value = value
        self.name = name

    @property
    def value(self):
        return NBTObject.value.fget(self)

    @value.setter
    def value(self, value):
        if not isinstance(value, int):
            raise TypeError('value must be an integer')
        if not (-128 <= value <= 127):
            raise ValueError("NBT Byte value must be between -128 and 127")
        NBTObject.value.fset(self, value)

    def serialize(self) -> bytearray:
        return bytearray(struct.pack(">b", self.value))

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("Invalid data for NBT Byte")
        offset += 1

        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        value = struct.unpack_from(">b", data, offset)[0]
        offset += 1

        if return_offset:
            return cls(name, value), offset
        return cls(name, value)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        if len(value) < 1:
            raise ValueError("NBT Byte value must be at least 1 bytes")
        if return_size:
            return cls("", struct.unpack_from(">b", value, 0)[0]), 1
        return cls("", struct.unpack_from(">b", value, 0)[0])


class Short(NBTObject):
    """表示NBT的Short类型"""
    TAG_ID = 0x02

    def __init__(self, name: str = "", value: int = 0):
        super().__init__(value, name)
        self.value = value
        self.name = name

    @property
    def value(self):
        return NBTObject.value.fget(self)

    @value.setter
    def value(self, value):
        if not isinstance(value, int):
            raise TypeError('value must be an integer')
        if not (-32768 <= value <= 32767):
            raise ValueError("NBT Short value must be between -32,768 and 32,767")
        NBTObject.value.fset(self, value)

    def serialize(self) -> bytearray:
        return bytearray(struct.pack(">h", self.value))

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("Invalid data for NBT Short")
        offset += 1

        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        value = struct.unpack_from(">h", data, offset)[0]
        offset += 2

        if return_offset:
            return cls(name, value), offset
        return cls(name, value)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        if len(value) < 2:
            raise ValueError("NBT Short value must be at least 2 bytes")
        if return_size:
            return cls("", struct.unpack_from(">h", value, 0)[0]), 2
        return cls("", struct.unpack_from(">h", value, 0)[0])


class Int(NBTObject):
    """表示NBT的Integer类型"""
    TAG_ID = 0x03

    def __init__(self, name: str = "", value: int = 0):
        super().__init__(value, name)
        self.value = value
        self.name = name

    @property
    def value(self):
        return NBTObject.value.fget(self)

    @value.setter
    def value(self, value):
        if not isinstance(value, int): raise TypeError('value must be an integer')
        if not (-2147483648 <= value <= 2147483647): raise ValueError(
            "NBT Int value must be between -2,147,483,648 and 2,147,483,647")
        NBTObject.value.fset(self, value)

    def serialize(self) -> bytearray:
        return bytearray(struct.pack(">i", self.value))

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("NBT Int value must be bytes")
        offset += 1

        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        value = struct.unpack_from(">i", data, offset)[0]
        offset += 4

        if return_offset:
            return cls(name, value), offset
        return cls(name, value)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        if len(value) < 4:
            raise ValueError("NBT Int value must be at least 4 bytes")
        if return_size:
            return cls("", struct.unpack_from(">i", value, 0)[0]), 4
        return cls("", struct.unpack_from(">i", value, 0)[0])


class Long(NBTObject):
    """表示NBT的Long类型"""
    TAG_ID = 0x04

    def __init__(self, name: str = "", value: int = 0):
        super().__init__(value, name)
        self.value = value
        self.name = name

    @property
    def value(self):
        return NBTObject.value.fget(self)

    @value.setter
    def value(self, value):
        if not isinstance(value, int):
            raise TypeError('value must be an integer')
        # 范围是 -2^63 到 2^63-1
        if not (-9223372036854775808 <= value <= 9223372036854775807):
            raise ValueError("NBT Long value exceeds the range of a 64-bit signed integer")
        NBTObject.value.fset(self, value)

    def serialize(self) -> bytearray:
        return bytearray(struct.pack(">q", self.value))

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("Invalid data for NBT Long")
        offset += 1

        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        value = struct.unpack_from(">q", data, offset)[0]
        offset += 8

        if return_offset:
            return cls(name, value), offset
        return cls(name, value)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        if len(value) < 8:
            raise ValueError("NBT Short value must be at least 8 bytes")
        if return_size:
            return cls("", struct.unpack_from(">q", value, 0)[0])
        return cls("", struct.unpack_from(">q", value, 0)[0]), 8


class Float(NBTObject):
    """表示NBT的Float类型"""
    TAG_ID = 0x05

    def __init__(self, name: str = "", value: float = 0.0):
        super().__init__(value, name)
        self.value = value
        self.name = name

    @property
    def value(self):
        return NBTObject.value.fget(self)

    @value.setter
    def value(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError('value must be a number (int or float)')
        # 转换为float，并限制在单精度浮点数的有效范围内
        value_float = float(value)
        if not (-3.4e38 <= value_float <= 3.4e38):
            raise ValueError("NBT Float value exceeds the range of a 32-bit single-precision float")
        NBTObject.value.fset(self, value_float)

    def serialize(self) -> bytearray:
        return bytearray(struct.pack(">f", self.value))

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("Invalid data for NBT Float")
        offset += 1

        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        value = struct.unpack_from(">f", data, offset)[0]
        offset += 4

        if return_offset:
            return cls(name, value), offset
        return cls(name, value)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        if len(value) < 4:
            raise ValueError("NBT Short value must be at least 2 bytes")
        if return_size:
            return cls("", struct.unpack_from(">f", value, 0)[0]), 4
        return cls("", struct.unpack_from(">f", value, 0)[0])


class Double(NBTObject):
    """表示NBT的Double类型"""
    TAG_ID = 0x06

    def __init__(self, name: str = "", value: float = 0.0):
        super().__init__(value, name)
        self.value = value
        self.name = name

    @property
    def value(self):
        return NBTObject.value.fget(self)

    @value.setter
    def value(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError('value must be a number (int or float)')
        # 转换为float, 在Python float的表示范围内
        value_float = float(value)
        NBTObject.value.fset(self, value_float)

    def serialize(self) -> bytearray:
        return bytearray(struct.pack(">d", self.value))

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("Invalid data for NBT Double")
        offset += 1

        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        value = struct.unpack_from(">d", data, offset)[0]
        offset += 8

        if return_offset:
            return cls(name, value), offset
        return cls(name, value)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        if len(value) < 8:
            raise ValueError("NBT Short value must be at least 8 bytes")
        if return_size:
            return cls("", struct.unpack_from(">d", value, 0)[0]), 8
        return cls("", struct.unpack_from(">d", value, 0)[0])


class ByteArray(NBTObject):
    """表示NBT的ByteArray类型"""
    TAG_ID = 0x07

    def __init__(self, name: str = "", value: bytes = b""):
        super().__init__(value, name)
        self.value = value
        self.name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, (bytes, bytearray)):
            raise TypeError('value must be bytes or bytearray')
        # 长度检查 (根据JVM实现，最大值可能在2,147,483,639到2,147,483,647之间)
        if len(value) > 2147483647:
            raise ValueError("ByteArray length exceeds maximum limit")
        self._value = bytes(value)  # 确保是不可变的bytes

    def serialize(self) -> bytearray:
        # 序列化: 长度 (4字节, 大端序) + 字节数据
        data = bytearray()
        data.extend(struct.pack(">i", len(self.value)))  # 长度
        data.extend(self.value)  # 字节数据本身
        return data

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("Invalid data for NBT ByteArray")
        offset += 1

        # 读取名称
        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        # 读取数组长度
        array_length = struct.unpack_from(">i", data, offset)[0]
        offset += 4
        # 读取字节数据
        value = bytes(data[offset:offset + array_length])
        offset += array_length

        if return_offset:
            return cls(name, value), offset
        return cls(name, value)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        length = struct.unpack_from(">i", value, 0)[0]
        offset = 4
        if return_size:
            return cls("", value[offset:offset + length]), 4 + length
        return cls("", value[offset:offset + length])


class String(NBTObject):
    """表示NBT的String类型"""
    TAG_ID = 0x08

    def __init__(self, name: str = "", value: str = ""):
        super().__init__(value, name)
        self.value = value
        self.name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, (str, bytearray, bytes)):
            raise TypeError('value must be a string')
        if isinstance(value, (bytes, bytearray)):
            self._value = bytes(value).decode("utf-8")
            return
        self._value = str(value)

    def serialize(self) -> bytearray:
        data = bytearray()
        # 将字符串编码为UTF-8字节
        encoded_str = self.value.encode('utf-8')
        # 序列化: 长度 (2字节无符号短整型, 大端序) + UTF-8字节数据
        data.extend(struct.pack(">H", len(encoded_str)))  # 长度
        data.extend(encoded_str)  # 字符串数据本身
        return data

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("Invalid data for NBT String")
        offset += 1

        # 读取标签名称
        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        # 读取字符串长度 (无符号短整型)
        str_length = struct.unpack_from(">H", data, offset)[0]
        offset += 2
        # 读取字符串字节数据并解码
        value = data[offset:offset + str_length].decode("utf-8")
        offset += str_length

        if return_offset:
            return cls(name, value), offset
        return cls(name, value)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        length = struct.unpack_from(">H", value, 0)[0]
        offset = 2
        if return_size:
            return cls("", value[offset:offset + length]), 2 + length
        return cls("", value[offset:offset + length])


class List(NBTObject):
    """表示NBT的List类型。列表中的所有元素必须是同一类型的NBTObject。"""
    TAG_ID = 0x09

    def __init__(self, name: str = "", value: list[NBTObject] = None):
        if value is None:
            value = []
        super().__init__(value, name)
        self.value = value  # 使用setter进行验证
        self.name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: list[NBTObject]):
        if not isinstance(value, list):
            raise TypeError('value must be a list')
        if value and not all(isinstance(item, IdToNbt(item.TAG_ID)) for item in value):
            raise TypeError('All elements in a NBT List must be of the same type')
        self._value = value

    def serialize(self) -> bytearray:
        data = bytearray()
        if not self.value:
            # 空列表的元素类型可以视为TAG_End
            data.append(0x00)  # 元素类型ID
            data.extend(struct.pack(">i", 0))  # 长度为0
            return data

        # 添加元素类型ID
        data.append(self.value[0].TAG_ID)
        # 添加列表长度
        data.extend(struct.pack(">i", len(self.value)))
        # 序列化每个元素（只序列化其负载payload，即serialize()返回的数据）
        for item in self.value:
            data.extend(item.serialize())  # 注意：列表中的元素没有名称！
        return data

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("Invalid data for NBT List")
        offset += 1

        # 读取标签名称
        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        # 读取元素类型ID
        element_type_id = data[offset]
        offset += 1
        # 读取列表长度
        list_length = struct.unpack_from(">i", data, offset)[0]
        offset += 4

        elements = []
        # 根据元素类型ID，获取对应的NBTObject子类
        # 你需要一个映射关系：TAG_ID -> Class (例如 {0x01: Byte, 0x03: Int, ...})
        # 这里假设有一个全局字典 TAG_ID_TO_CLASS
        element_class = IdToNbt(element_type_id)
        if element_class is None and element_type_id != 0x00:  # TAG_End
            raise ValueError(f"Unsupported element type ID in List: 0x{element_type_id:02x}")

        # 反序列化每个元素
        for _ in range(list_length):
            element, size = element_class.fromValue(data[offset:], return_size=True)
            offset += size
            elements.append(element)
            # raise NotImplementedError("List element deserialization requires internal design consideration.")

        if return_offset:
            return cls(name, elements), offset
        return cls(name, elements)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        element_id = value[0]
        list_length = struct.unpack_from(">i", value, 1)[0]
        offset = 5
        element_class = IdToNbt(element_id)
        elements = []
        for _ in range(list_length):
            e, _o = element_class.fromValue(value[offset::], return_size=True)
            # print(e, _o)
            elements.append(e)
            offset += _o
        if return_size:
            return cls("", elements), offset
        return cls("", elements)

    def append(self, other: NBTObject):
        if not isinstance(other, NBTObject): raise TypeError('other must be a NBTObject')
        self.value.append(other)

    def __add__(self, other: NBTObject):
        self.append(other)
        return self


class Compound(NBTObject):
    TAG_ID = 0x0A

    def __init__(self, name: str = "", *value: NBTObject):
        super().__init__(value, name)
        self._value = {}
        self.name = name
        self.value = value

    @property
    def value(self) -> dict[str, NBTObject]:
        return NBTObject.value.fget(self)

    @value.setter
    def value(self, value):
        for nbt in value:
            if not isinstance(nbt, NBTObject): raise TypeError("value must be an NBTObject")
            self._value[nbt.name] = nbt

    def pop_tag(self, name: str):
        if not isinstance(name, str): raise TypeError("name must be string")
        self._value.pop(name, None)

    def serialize(self) -> bytearray:
        data = bytearray()

        data += serialize(*self.value.values(), compress=False)

        data.append(0x00)
        return data

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("NBT Int value must be bytes")
        offset += 1

        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        tags = []

        while ...:
            tag_class = IdToNbt(data[offset])
            if tag_class == End: break
            tag, _o = tag_class.deserialize(data[offset::], return_offset=True)
            offset += _o
            tags.append(tag)
        if return_offset: return cls(name, *tags), offset + 1
        return cls(name, *tags)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        offset = 0
        tags = []
        size = 0
        while ...:
            tag_id = value[offset]
            if tag_id == 0x00: break
            _class = IdToNbt(tag_id)
            tag, _size = _class.deserialize(value[offset::], return_offset=True)
            tags.append(tag)
            offset += _size
            size += _size

        if return_size:
            return cls("", *tags), size + 1
        return cls("", *tags)

    def __getitem__(self, name: str) -> NBTObject:
        if not isinstance(name, str): raise TypeError("name must be string")
        return self.value[name]

    def __add__(self, other: 'NBTObject') -> 'NBTObject':
        if not isinstance(other, NBTObject): raise TypeError("other must be an NBTObject")
        return Compound(self.name, *(self.value | {other.name: other}).values())


class IntArray(NBTObject):
    """表示NBT的IntArray类型"""
    TAG_ID = 0x0B

    def __init__(self, name: str = "", value: list[int] = None):
        if value is None:
            value = []
        super().__init__(value, name)
        self.value = value
        self.name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, list):
            raise TypeError('value must be a list of integers')
        if not all(isinstance(item, int) for item in value):
            raise TypeError('All items in IntArray must be integers')
        # 长度检查
        if len(value) > 2147483647:
            raise ValueError("IntArray length exceeds maximum limit")
        self._value = value

    def serialize(self) -> bytearray:
        data = bytearray()
        data.extend(struct.pack(">i", len(self.value)))  # 长度
        # 打包所有整数值
        for num in self.value:
            data.extend(struct.pack(">i", num))
        return data

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("Invalid data for NBT IntArray")
        offset += 1

        # 读取名称
        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        # 读取数组长度
        array_length = struct.unpack_from(">i", data, offset)[0]
        offset += 4

        value = []
        # 读取array_length个整型值
        for _ in range(array_length):
            int_val = struct.unpack_from(">i", data, offset)[0]
            value.append(int_val)
            offset += 4

        if return_offset:
            return cls(name, value), offset
        return cls(name, value)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        offset, size = 0, 0
        if len(value) < 4:
            raise ValueError("Insufficient data for IntArray length.")
        array_length = struct.unpack_from(">i", value, offset)[0]
        offset += 4
        size += 4

        if len(value) < offset + array_length * 4:
            raise ValueError("Insufficient data for IntArray elements.")

        # 3. 读取array_length个整型值
        value = []
        for _ in range(array_length):
            int_val = struct.unpack_from(">i", value, offset)[0]
            value.append(int_val)
            offset += 4
            size += 4

        if return_size:
            return cls("", value), size
        return cls("", value)


class LongArray(NBTObject):
    """表示NBT的LongArray类型"""
    TAG_ID = 0x0C

    def __init__(self, name: str = "", value: list[int] = None):
        if value is None:
            value = []
        super().__init__(value, name)
        self.value = value
        self.name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, list):
            raise TypeError('value must be a list of integers')
        if not all(isinstance(item, int) for item in value):
            raise TypeError('All items in LongArray must be integers')
        # 长度检查[1](@ref)
        if len(value) > 2147483647:
            raise ValueError("LongArray length exceeds maximum limit")
        self._value = value

    def serialize(self) -> bytearray:
        data = bytearray()
        data.extend(struct.pack(">i", len(self.value)))  # 长度
        # 打包所有长整数值
        for num in self.value:
            data.extend(struct.pack(">q", num))
        return data

    @classmethod
    def deserialize(cls, data: bytearray, return_offset: bool = False) -> 'NBTObject' | Tuple['NBTObject', int]:
        offset = 0
        if data[offset] != cls.TAG_ID:
            raise ValueError("Invalid data for NBT LongArray")
        offset += 1

        # 读取名称
        name_length = struct.unpack_from('>H', data, offset)[0]
        offset += 2
        name = data[offset:offset + name_length].decode("utf-8")
        offset += name_length

        # 读取数组长度
        array_length = struct.unpack_from(">i", data, offset)[0]
        offset += 4

        value = []
        # 读取array_length个长整型值
        for _ in range(array_length):
            long_val = struct.unpack_from(">q", data, offset)[0]
            value.append(long_val)
            offset += 8

        if return_offset:
            return cls(name, value), offset
        return cls(name, value)

    @classmethod
    def fromValue(cls, value: bytearray, return_size: bool = False) -> 'NBTObject':
        offset, size = 0, 0
        if len(value) < 4:
            raise ValueError("Insufficient data for IntArray length.")
        array_length = struct.unpack_from(">i", value, offset)[0]
        offset += 4
        size += 4

        if len(value) < offset + array_length * 8:
            raise ValueError("Insufficient data for LongArray elements.")

        # 3. 读取array_length个整型值
        value = []
        for _ in range(array_length):
            int_val = struct.unpack_from(">q", value, offset)[0]
            value.append(int_val)
            offset += 8
            size += 8

        if return_size:
            return cls("", value), size
        return cls("", value)


def serialize(*data: NBTObject, compress: bool = True, compression_level: int = None) -> bytearray:
    bytedata = bytearray()
    for obj in data:
        if isinstance(obj, NBTObject):
            bytedata += bytearray(bytes([obj.TAG_ID]))

            name = obj.name.encode("utf-8")
            bytedata += bytearray(struct.pack(">H", len(name)))
            bytedata += name

            bytedata += obj.serialize()

    if not compress:
        return bytedata

    if compression_level is not None:
        compression_level = compression_level
    elif len(bytedata) < 100 * 1024:  # data < 100KB
        compression_level = 1
    elif len(bytedata) < 10 * 1024 * 1024:  # 100KB < data < 10MB
        compression_level = 5
    else:
        compression_level = 6

    return gzip.compress(bytedata, compresslevel=compression_level)


def deserialize(data: bytearray, compress: bool = True):
    if compress:
        data = gzip.decompress(data)
    _class = IdToNbt(data[0])
    obj = _class.deserialize(data)
    return obj


def print_nbt(nbt_obj, indent: int = 0, indent_str: str = "\t"):
    """
    格式化打印一个 NBTObject，展示其层次结构。

    Args:
        nbt_obj: 要打印的 NBTObject 实例（例如 Compound, List, Int, String, Float 等）。
        indent: 当前的缩进级别。默认为 0。
        indent_str: 用于每一级缩进的字符串。默认为四个空格。
    """
    # 根据对象类型进行不同的格式化处理
    if isinstance(nbt_obj, Compound):
        # 打印 Compound 的开始，显示其名称（如果存在）
        print(f"Compound: {{")
        # 递归打印 Compound 中的每一个子标签
        for name, tag in nbt_obj.value.items():
            # 先打印出键和冒号，但不换行
            print(f"{indent_str * (indent + 1)}'{name}': ", end="")
            # 然后递归打印值，这个调用会根据值的类型自行决定如何换行
            print_nbt(tag, indent + 1)
        # 打印 Compound 的结束
        print(f"{indent_str * indent}}}")
    elif isinstance(nbt_obj, List):
        # 确定列表元素的类型名称
        element_type = type(nbt_obj.value[0]).__name__ if nbt_obj.value else "Empty"
        # 打印 List 的开始，显示其名称（如果存在）和元素类型
        # 修改这里：直接显示 List('B') [String]: [，注意括号和空格

        print(f"List [{element_type}]:", '[' if element_type != "Empty" else '[]')
        # 遍历并打印 List 中的每一个元素
        for i, element in enumerate(nbt_obj.value):
            # 打印索引和冒号，但不换行
            print(f"{indent_str * (indent + 1)}[{i}]: ", end="")
            # 递归打印元素值
            print_nbt(element, indent + 1, indent_str)
        # 打印 List 的结束
        if element_type != "Empty":
            print(f"{indent_str * indent}]")
    elif isinstance(nbt_obj, String):
        # 对于 String 类型，使用 String("value") 格式
        # 使用 repr() 确保字符串中的特殊字符被正确转义和显示
        print(f"String({repr(nbt_obj.value)})")
    elif isinstance(nbt_obj, (Int, Float, Byte, Short, Long, Double)):
        # 对于数字类型，使用 Type(value) 格式
        type_name = nbt_obj.__class__.__name__
        print(f"{type_name}({nbt_obj.value})")
    else:
        # 对于其他未明确处理的类型，也尝试以 Type(value) 格式显示
        type_name = nbt_obj.__class__.__name__
        print(f"{type_name}({nbt_obj.value})")


def json_to_nbt(nbt_obj: dict[str, NBTObject] | list) -> NBTObject:
    if isinstance(nbt_obj, dict):
        nbt = Compound("")
        for name, tag in nbt_obj.items():
            if type(tag) is dict or type(tag) is list:
                _n = json_to_nbt(tag)
                _n.name = name
                nbt += _n
            elif type(tag) is bool:
                nbt += Byte(name, tag + 0)
            elif type(tag) is float:
                nbt += Float(name, tag)
            elif type(tag) is int:
                nbt += Int(name, tag)
            elif type(tag) is str:
                nbt += String(name, tag)
    elif isinstance(nbt_obj, list):
        nbt = List("")
        for tag in nbt_obj:
            if type(tag) is dict or type(tag) is list:
                nbt += json_to_nbt(tag)
            elif type(tag) is bool:
                nbt += Byte("", tag + 0)
            elif type(tag) is float:
                nbt += Float("", tag)
            elif type(tag) is int:
                nbt += Int("", tag)
            elif type(tag) is str:
                nbt += String("", tag)
    else:
        return
    return nbt

def cout_nbt(nbt_obj: NBTObject, index=0):
    if len(str(nbt_obj.value)) > 30:
        print(f"{'\t' * index}{nbt_obj.__class__.__name__}(\"{nbt_obj.name}\", ")
        if isinstance(nbt_obj, Compound):
            for name, tag in nbt_obj.value.items():
                cout_nbt(tag, index+1)
        elif isinstance(nbt_obj, List):
            print(f"{'\t' * index}[")
            for i in nbt_obj.value:
                cout_nbt(i, index + 1)
            print(f"{'\t' * index}]")
        else:
            print(f"{'\t' * (index + 1)}{nbt_obj.value}")
        print(f"{'\t' * index}),")
    else:
        print(f"{'\t' * index}{nbt_obj.__class__.__name__}(\"{nbt_obj.name}\", {nbt_obj.value}),")

__all__ = ['End', 'Byte', 'Short', 'Int', 'Long', 'Float', 'Double', 'ByteArray', 'String', 'List', 'Compound', 'IntArray', 'LongArray', 'NBTObject', 'serialize', 'deserialize', 'print_nbt', 'IdToNbt', 'json_to_nbt']

# __all__ = [cls.__name__ for cls in NBTObject.__subclasses__()] + [NBTObject.__name__, serialize.__name__,
#                                                                   deserialize.__name__, print_nbt.__name__,
#                                                                   IdToNbt.__name__, json_to_nbt.__name__]
# print(__all__)

if __name__ == '__main__':
    n = Compound("",
                 Int("A", 114)
                 )

    data = Compound("",
                    Compound(
                        "minecraft:dimension_type",
                        String("type", "minecraft:dimension_type"),
                        List("value", [
                            Compound("",
                                     String("id", "minecraft:overworld"),
                                     Compound("element",
                                              Byte("piglin_safe", 0),  # false -> 0
                                              Byte("natural", 1),  # true -> 1
                                              Float("ambient_light", 0.0),
                                              Long("fixed_time", 0),
                                              String("infiniburn", "#minecraft:infiniburn_overworld"),
                                              Byte("respawn_anchor_works", 0),  # false -> 0
                                              Byte("has_skylight", 1),  # true -> 1
                                              Byte("bed_works", 1),  # true -> 1
                                              String("effects", "minecraft:overworld"),
                                              Byte("has_raids", 1),  # true -> 1
                                              Int("min_y", -64),
                                              Int("height", 384),
                                              Int("logical_height", 384),
                                              Double("coordinate_scale", 1.0),
                                              Byte("ultrawarm", 0),  # false -> 0
                                              Byte("has_ceiling", 0)  # false -> 0
                                              )
                                     )
                        ])
                    ),
                    Compound(
                        "minecraft:worldgen/biome",
                        String("type", "minecraft:worldgen/biome"),
                        List("value", [
                            Compound("",
                                     String("id", "minecraft:plains"),
                                     Compound("element",
                                              String("precipitation", "rain"),
                                              Float("temperature", 0.8),
                                              Float("downfall", 0.4),
                                              Compound("effects",
                                                       Int("sky_color", 7907327),
                                                       Int("fog_color", 12638463),
                                                       Int("water_color", 4159204),
                                                       Int("water_fog_color", 329011)
                                                       )
                                              )
                                     )
                        ])
                    ))

    with open("a.nbt", "wb") as f:
        f.write(serialize(data))

    # print_nbt(n)
    print(serialize(data, compress=False))

# \n\x00\x00\n\x00\x18minecraft:dimension_type\x08\x00\x04type\x00\x18minecraft:dimension_type\t\x00\x05value\n\x00\x00\x00\x01\x08\x00\x02id\x00\x13minecraft:overworld\n\x00\x07element\x01\x00\x0bpiglin_safe\x00\x01\x00\x07natural\x01\x05\x00\rambient_light\x00\x00\x00\x00\x04\x00\nfixed_time\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\ninfiniburn\x00\x1f#minecraft:infiniburn_overworld\x01\x00\x14respawn_anchor_works\x00\x01\x00\x0chas_skylight\x01\x01\x00\tbed_works\x01\x08\x00\x07effects\x00\x13minecraft:overworld\x01\x00\thas_raids\x01\x03\x00\x05min_y\xff\xff\xff\xc0\x03\x00\x06height\x00\x00\x01\x80\x03\x00\x0elogical_height\x00\x00\x01\x80\x06\x00\x10coordinate_scale?\xf0\x00\x00\x00\x00\x00\x00\x01\x00\tultrawarm\x00\x01\x00\x0bhas_ceiling\x00\x00\x00\x00\n\x00\x18minecraft:worldgen/biome\x08\x00\x04type\x00\x18minecraft:worldgen/biome\t\x00\x05value\n\x00\x00\x00\x01\x08\x00\x02id\x00\x10minecraft:plains\n\x00\x07element\x08\x00\rprecipitation\x00\x04rain\x05\x00\x0btemperature?L\xcc\xcd\x05\x00\x08downfall>\xcc\xcc\xcd\n\x00\x07effects\x03\x00\tsky_color\x00x\xa7\xff\x03\x00\tfog_color\x00\xc0\xd8\xff\x03\x00\x0bwater_color\x00?v\xe4\x03\x00\x0fwater_fog_color\x00\x05\x053\x00\x00\x00\x00\x00
