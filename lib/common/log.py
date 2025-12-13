# -*- coding: utf-8 -*-
import logging
import os
import sys
import ctypes
import codecs

# -------------------- 控制台颜色常量（Windows） --------------------
FOREGROUND_WHITE = 0x0007
FOREGROUND_BLUE = 0x01
FOREGROUND_GREEN = 0x02
FOREGROUND_RED = 0x04
FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN

STD_OUTPUT_HANDLE = -11
try:
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
except Exception:
    std_out_handle = None

try:
    unicode
except NameError:
    unicode = str


def set_color(color, handle=std_out_handle):
    """设置控制台颜色"""
    if handle:
        try:
            ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        except Exception:
            pass


# -------------------- 安全 FileHandler（兼容 Py2） --------------------
class SafeFileHandler(logging.FileHandler):
    """Python2 下强制使用 UTF-8 写入，避免 IOError"""
    def __init__(self, filename, mode='a', encoding='utf-8'):
        if sys.version_info[0] < 3:
            stream = codecs.open(filename, mode, encoding)
            logging.StreamHandler.__init__(self, stream)
        else:
            logging.FileHandler.__init__(self, filename, mode, encoding)


# -------------------- 主 Logger 类 --------------------
class Logger(object):

    def __init__(self, path, clevel=logging.INFO, flevel=logging.DEBUG):
        self.path = path
        self._make_dir()

        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)

        # 清理旧 handler
        for h in list(self.logger.handlers):
            self.logger.removeHandler(h)

        fmt = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )

        # 控制台输出
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(clevel)

        # 文件输出
        if sys.version_info[0] >= 3:
            fh = logging.FileHandler(self.path, encoding='utf-8')
        else:
            fh = SafeFileHandler(self.path, 'a', encoding='utf-8')

        fh.setFormatter(fmt)
        fh.setLevel(flevel)

        self.logger.addHandler(sh)
        self.logger.addHandler(fh)

    # ------------------------------------------------------------------
    def _make_dir(self):
        folder = os.path.dirname(self.path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)

    # ------------------------------------------------------------------
    def debug(self, message):
        set_color(FOREGROUND_BLUE)
        self.logger.debug(self._to_str(message))
        set_color(FOREGROUND_WHITE)

    def info(self, message):
        set_color(FOREGROUND_WHITE)
        self.logger.info(self._to_str(message))

    def warn(self, message, color=FOREGROUND_YELLOW):
        set_color(color)
        self.logger.warning(self._to_str(message))
        set_color(FOREGROUND_WHITE)

    def error(self, message, color=FOREGROUND_RED):
        if not message:
            message = 'Unknown Error'
        set_color(color)
        self.logger.error(self._to_str(message))
        set_color(FOREGROUND_WHITE)

    def critical(self, message):
        set_color(FOREGROUND_RED)
        self.logger.critical(self._to_str(message))
        set_color(FOREGROUND_WHITE)

    # ------------------------------------------------------------------
    def _to_str(self, message):
        """统一字符串处理，防止 Python2 UnicodeDecodeError"""
        try:
            if sys.version_info[0] >= 3:
                return str(message)
            else:
                # ✅ Python2 返回 unicode，防止 ascii 解码错误
                if isinstance(message, unicode):
                    return message
                elif isinstance(message, str):
                    return message.decode('utf-8', 'ignore')
                else:
                    return unicode(message)
        except Exception as e:
            try:
                return u'<<ENCODE ERROR: {}>>'.format(e)
            except:
                return u'ENCODE ERROR'

    # ------------------------------------------------------------------
    def get_errors(self):
        """读取日志文件中包含 [ERROR] 的行"""
        errors = []
        if not os.path.exists(self.path):
            return errors

        if sys.version_info[0] >= 3:
            f = open(self.path, "r", encoding="utf-8", errors="ignore")
        else:
            f = codecs.open(self.path, "r", "utf-8", errors="ignore")

        with f:
            for line in f:
                if "[ERROR]" in line:
                    errors.append(line.strip())
        return errors


# -------------------- 工具函数 --------------------
def _read_info(path):
    if not os.path.exists(path):
        return None

    if sys.version_info[0] >= 3:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        with codecs.open(path, "r", "utf-8", errors="ignore") as f:
            return f.read()


def read_info(path):
    data = _read_info(path)
    return data.splitlines() if data else []


# # -------------------- 示例 --------------------
# if __name__ == '__main__':
#     log = Logger(r'D:\test_log\demo_log.log')
#     log.info(u"程序启动成功")
#     log.warn(u"警告：缺少配置文件")
#     log.error(u"错误：无法连接数据库 😅")
#     log.debug(u"调试信息：变量x=123，路径=D:/test")
#
#     print("\n错误日志内容：")
#     for e in log.get_errors():
#         print(e)
