import struct
from datetime import datetime, UTC


class Region:
    """
    用于读取Minecraft .mca区域文件头的类。

    Attributes:
        data (bytearray): 整个.mca文件的二进制数据。
        chunk_offsets (list): 存储1024个区块的位置偏移和扇区数量。
        timestamps (list): 存储1024个区块的最后修改时间。
    """

    def __init__(self, data):
        """
        使用给定的bytearray数据初始化Region对象。

        Args:
            data (bytearray): .mca文件的二进制数据。
        """
        self.data = data
        self.chunk_offsets = []  # 每个元素为元组 (sector_offset, sector_count)
        self.timestamps = []  # 每个元素为datetime对象

        self._parse_header()

    def _parse_header(self):
        """解析MCA文件的前8KB文件头，包括区块位置表和时间戳表。"""
        # 确保数据足够长
        if len(self.data) < 8192:
            raise ValueError("提供的字节数组数据不足以包含完整的MCA文件头（需要至少8192字节）")

        # 解析区块位置表 (前4KB)
        for i in range(1024):
            start = i * 4
            end = start + 4
            entry_bytes = self.data[start:end]

            # 前3字节为大端序扇区偏移量
            sector_offset = int.from_bytes(entry_bytes[:3], byteorder='big')
            # 第4字节为扇区数量
            sector_count = entry_bytes[3]

            self.chunk_offsets.append((sector_offset, sector_count))

        # 解析时间戳表 (后4KB)
        for i in range(1024):
            start = 4096 + i * 4  # 时间戳表从4KB偏移开始
            end = start + 4
            timestamp_bytes = self.data[start:end]

            # 将4字节大端序数据转换为无符号整数
            timestamp_int = struct.unpack('>I', timestamp_bytes)[0]
            # 将Unix时间戳转换为datetime对象，如果为0则保持None
            timestamp_dt = datetime.fromtimestamp(timestamp_int, tz=UTC) if timestamp_int != 0 else None

            self.timestamps.append(timestamp_dt)

    def get_chunk_offset(self, chunk_x, chunk_z):
        """
        获取指定区块坐标的位置偏移和扇区数量。

        Args:
            chunk_x (int): 区块在区域内的X坐标 (0-31)。
            chunk_z (int): 区块在区域内的Z坐标 (0-31)。

        Returns:
            tuple: (sector_offset, sector_count)
        """
        index = self._get_chunk_index(chunk_x, chunk_z)
        return self.chunk_offsets[index]

    def get_timestamp(self, chunk_x, chunk_z):
        """
        获取指定区块坐标的最后修改时间。

        Args:
            chunk_x (int): 区块在区域内的X坐标 (0-31)。
            chunk_z (int): 区块在区域内的Z坐标 (0-31)。

        Returns:
            datetime: 区块的最后修改时间，如果区块不存在则为None。
        """
        index = self._get_chunk_index(chunk_x, chunk_z)
        return self.timestamps[index]

    def _get_chunk_index(self, chunk_x, chunk_z):
        """
        将区块的二维坐标 (x, z) 转换为一维索引 (0-1023)。

        Args:
            chunk_x (int): 区块在区域内的X坐标 (0-31)。
            chunk_z (int): 区块在区域内的Z坐标 (0-31)。

        Returns:
            int: 区块在数组中的索引。
        """
        if not (0 <= chunk_x < 32 and 0 <= chunk_z < 32):
            raise ValueError("区块坐标必须在0到31之间")
        return chunk_z * 32 + chunk_x


# 示例用法
if __name__ == "__main__":
    # 假设你已经将.r.0.0.mca文件的内容读入了一个bytearray
    # 例如：with open('r.0.0.mca', 'rb') as f:
    #          data = bytearray(f.read())

    # 为了演示，我们创建一个虚拟的bytearray（实际使用时请从文件读取）
    # dummy_data = bytearray(8192)  # 创建一个最小8KB的文件头
    # 设置一些示例值（实际数据会更复杂）
    # dummy_data[0:3] = int(2).to_bytes(3, 'big')  # 第一个区块的扇区偏移量为2
    # dummy_data[3] = 1  # 第一个区块占用1个扇区
    # 设置一个时间戳 (2023-10-01 12:00:00 UTC)
    # example_timestamp = int(datetime(2023, 10, 1, 12, 0, 0).timestamp())
    # dummy_data[4096:4100] = struct.pack('>I', example_timestamp)  # 第一个区块的时间戳

    with open("r.0.0.mca", "rb") as f:
        dummy_data = f.read()

    # 创建Region对象
    region = Region(dummy_data)

    # 获取第一个区块 (x=0, z=0) 的信息
    offset, count = region.get_chunk_offset(0, 0)
    timestamp = region.get_timestamp(0, 0)

    print(f"区块 (0, 0) 的扇区偏移量: {offset}")
    print(f"区块 (0, 0) 占用的扇区数: {count}")
    print(f"区块 (0, 0) 的最后修改时间: {timestamp}")

    # 检查另一个可能不存在的区块 (例如 x=1, z=1)
    offset, count = region.get_chunk_offset(1, 1)
    timestamp = region.get_timestamp(1, 1)
    print(f"\n区块 (1, 1) 的扇区偏移量: {offset} (0表示区块未生成)")
    print(f"区块 (1, 1) 的最后修改时间: {timestamp} (None表示区块未生成)")
