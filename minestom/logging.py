import sys
import threading
import inspect
from datetime import datetime
from enum import Enum, unique

@unique
class Color(Enum):
    INFO = "\033[1;37m"     # 白色加粗
    ERROR = "\033[1;31m"    # 红色加粗
    WARNING = "\033[1;33m"  # 黄色加粗
    LOG = "\033[1;34m"      # 蓝色加粗
    DEBUG = "\033[1;32m"    # 绿色加粗
    RESET = "\033[0m"

class Logging:
    def _time_str(self):
        return datetime.now().strftime("%H:%M:%S")

    def _get_caller_info(self):
        stack = inspect.stack()
        for frame_info in stack[2:]:
            filename = frame_info.filename
            if filename != __file__:
                return filename, frame_info.lineno
        frame_info = stack[2]
        return frame_info.filename, frame_info.lineno

    def _format_message(self, level, msg, thread_name="Main"):
        time_str = self._time_str()
        if level in ("debug", "log"):
            filename, lineno = self._get_caller_info()
            short_filename = filename.split("/")[-1].split("\\")[-1]
            return f"[{time_str}] [{short_filename}] [line {lineno}]: {msg}"
        else:
            if not thread_name:
                thread_name = "Main"
            return f"[{time_str}] [{thread_name}] {msg}"
    def _print(self, level, msg, thread_name="Main"):
        color_map = {
            "info": Color.INFO,
            "error": Color.ERROR,
            "warning": Color.WARNING,
            "log": Color.LOG,
            "debug": Color.DEBUG,
        }
        color = color_map.get(level, Color.RESET).value
        formatted_msg = self._format_message(level, " ".join([str(m) for m in msg]), thread_name)
        print(f"{color}{formatted_msg}{Color.RESET.value}", file=sys.stdout)

    def info(self, *msg, thread_name="Main"):
        self._print("info", msg, thread_name)

    def error(self, *msg, thread_name="Main"):
        self._print("error", msg, thread_name)

    def warning(self, *msg, thread_name="Main"):
        self._print("warning", msg, thread_name)

    def log(self, *msg):
        self._print("log", msg)

    def debug(self, *msg):
        self._print("debug", msg)
