import random
import socket
import time
import traceback
import uuid
import zlib
from threading import Thread

from minestom.Minecraft import MinecraftConfig
from minestom.Packet import *
from minestom.Packet.PacketBase import ServerPacket
from minestom.PacketType import decode_varint, encode_varint, encode_string
from minestom.logging import Logging
from minestom.utils import create_simple_heightmap, create_simple_chunk_data

def DataFormat(data):
    return ' '.join([data.hex().upper()[i:i+2] for i in range(0, len(data.hex().upper()), 2)])

class MinecraftServer:
    def __init__(self, _config: MinecraftConfig = MinecraftConfig()):
        self.online = 2**31
        self._config = _config
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._threshold = -1
        self.logger = Logging()

    def play(self, _c: socket.socket):
        try:
            # 发送加入游戏包
            self._send(_c, 0x28, ServerJoinGamePacket(entity_id=1))

            # 发送出生点位置
            self._send(_c, 0x4E, ServerSpawnPositionPacket())

            # 发送玩家初始位置和视角
            self._send(_c, 0x38, ServerPlayerPositionLookPacket(PlayerPosition(
                x=0.5, y=65.0, z=0.5,
                yaw=0.0, pitch=0.0,
                flags=0x00,
                teleport_id=1
            )))

            # 更新玩家区块位置
            self._send(_c, 0x49, ServerUpdateViewPositionPacket(ChunkLocation(chunk_x=0, chunk_z=0)))

            # 发送初始区块
            chunk_packet = ServerChunkDataPacket(
                chunk_x=0,
                chunk_z=0,
                heightmaps=create_simple_heightmap(),
                chunk_data=create_simple_chunk_data(0, 0),
            )
            self._send(_c, 0x22, chunk_packet)

            # 发送玩家能力
            self._send(_c, 0x32, ServerPlayerAbilitiesPacket(
                flags=0x0f  # 创造模式 + 飞行
            ))

            # 添加玩家到列表
            self._send(_c, 0x36, ServerPlayerInfoPacket(
                action=0,
                uuid=uuid.uuid4(),
                name="Player",
                properties=[],
                gamemode=1,
                ping=0,
                has_display_name=False
            ))

            # 更新生命值
            self._send(_c, 0x52, ServerUpdateHealthPacket(
                health=20.0,
                food=20,
                food_saturation=5.0
            ))

            # 发送品牌信息
            self._send(_c, 0x19, ServerPluginMessagePacket(
                channel="minecraft:brand",
                data="CustomServer".encode('utf-8')
            ))

            # 发送初始时间
            self._send(_c, 0x5E, ServerTimeUpdatePacket(
                world_age=0,
                time_of_day=6000
            ))

            # 启动心跳
            self.start_keepalive(_c)

            # 主循环
            while True:
                length = self.recv_length(_c)
                if length == 0:
                    break

                data = _c.recv(length)
                packet_id = decode_varint(data)

                # 处理心跳响应
                if packet_id == 0x10:
                    # 保持连接
                    pass

                # 处理客户端设置
                elif packet_id == 0x08:
                    # 解析 ClientSettings 包
                    # [根据协议解析字段]
                    self.logger.info("收到客户端设置")

                # 处理位置更新
                elif packet_id in (0x13, 0x14, 0x15):
                    # 解析位置包
                    # [根据协议解析字段]
                    self.logger.info("收到位置更新")

        except ConnectionAbortedError:
            self.logger.warning("客户端断开连接")
        except Exception as e:
            # self.logger.error(f"游戏线程错误: {e}")
            # 获取详细的错误信息，包括文件名和行号
            tb = traceback.extract_tb(e.__traceback__)[-1]  # 获取最后一个堆栈帧
            filename = tb.filename
            lineno = tb.lineno
            self.logger.error(f"游戏线程错误: {e} (发生在 {filename} 第 {lineno} 行)")
        finally:
            _c.close()
            self.logger.info("连接关闭")

    def handle_play_packet(self, client, packet):
        # 1. 心跳响应 (0x10)
        if packet.packet_id == 0x10:
            # ClientKeepAlive 包处理
            pass

        # 2. 玩家位置更新 (0x13)
        elif packet.packet_id == 0x13:
            # ClientPlayerPosition 包处理
            pass

        # 3. 客户端设置 (0x08) - 重要!
        elif packet.packet_id == 0x08:
            # ClientSettings 包处理
            self.logger.info(f"客户端设置: {packet}")

        # 4. 传送确认 (0x00)
        elif packet.packet_id == 0x00:
            # ClientTeleportConfirm 包处理
            pass

    def start_keepalive(self, client):
        """启动心跳机制"""

        def keepalive_loop():
            while True:
                time.sleep(15)  # 每15秒发送一次
                keepalive_id = random.randint(1, 2147483647)
                try:
                    self._send(client, 0x23, ServerKeepAlivePacket(keepalive_id))
                except:
                    break  # 连接已关闭

        Thread(target=keepalive_loop, daemon=True).start()

    # ServerKeepAlivePacket ServerTimeUpdatePacket ServerUpdateLightPacket

    def _send(self, _socket: socket.socket, *_data) -> None:
        """自动包装数据为Minecraft格式"""
        data = b''
        for i in _data:
            if isinstance(i, ServerPacket):
                packet = i
                i = i.to_bytes
            if isinstance(i, int):
                data += encode_varint(i)
            elif isinstance(i, str):
                data += encode_string(i)
            elif isinstance(i, bytes):
                data += encode_varint(len(i))
                data += i
        if 0 < self._threshold <= len(data):
            length = encode_varint(len(data))
            data = length + zlib.compress(data, level=-1)
        _socket.send(encode_varint(len(data)) + data)
        print(f"长度值: {encode_varint(len(data))} 实际数据: {data}")
        time.sleep(0.1)
        return encode_varint(len(data)) + data

    def client(self, _client: socket.socket, addr: tuple[str, int]):
        """客户端处理"""
        status = MinecraftStatus.HANDSHAKING  # 自动设置状态握手
        while ...:
            length = self.recv_length(_client)  # 拿一下数据包长度
            data = _client.recv(length)  # 哪一下数据包数据
            if not data:  # 如果客户端已经关闭
                _client.close()  # 关闭实例
                return  # 结束循环
            packet = parser_packet(data, status)  # 解析拿到的包
            if isinstance(packet, ClientHandshakingPacket):  # 握手包
                status = MinecraftStatus(packet.status)  # 设置对应状态
            elif isinstance(packet, ClientStatusRequestPacket):  # 状态请求包
                self._send(_client, 0x00, ServerStatusResponsePacket(self._config, self.online, []))  # 发送状态
            elif isinstance(packet, ClientStatusPingPacket):  # 状态请求Ping包
                _client.send(b'\x09' + packet.byte)  #  原封不动发送回去
            elif isinstance(packet, ClientLoginRequest):  #  登录请求包
                if self._threshold > 0:  # 如果压缩阈值开启(大于0)
                    self._send(_client, 0x03, ServerSetCompressionPacket(self._threshold))  # 发送压缩阈值包
                self._send(_client, 0x02, ServerLoginSuccessPacket(packet.player_name))  #  发送登录成功包
                # status = MinecraftStatus.PLAY
                Thread(target=self.play, args=(_client,)).start()  # 开登录函数
                # print("成功登录")
                return

    def recv_length(self, _socket: socket.socket):
        _data = b''
        while ...:
            data = _socket.recv(1)
            _data += data
            if not _data:
                return 0
            if not data[0] & 128:
                break
        return decode_varint(_data)

    def run(self, host: str = '127.0.0.1', port: int = 25565):
        self.logger.info("正在启动...")
        self._socket.bind((host, port))
        self._socket.listen(self._config.maxPlayers)
        self.logger.info(f"开始监听, 地址为 {host}:{port}")
        while ...:
            client, addr = self._socket.accept()
            Thread(target=self.client, args=(client, addr)).start()


if __name__ == '__main__':
    MinecraftServer().run()
