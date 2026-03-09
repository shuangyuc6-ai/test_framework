"""
统一日志工具
- 同时输出到控制台和文件
- 每次运行生成带时间戳的日志文件
"""
import logging
import os
from datetime import datetime

LOG_DIR = "reports/logs"
os.makedirs(LOG_DIR, exist_ok=True)

_log_file = os.path.join(LOG_DIR, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
_initialized = False


def get_logger(name: str) -> logging.Logger:
    global _initialized
    logger = logging.getLogger(name)

    if not _initialized:
        logger.setLevel(logging.DEBUG)

        fmt = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
            datefmt="%H:%M:%S"
        )

        # 控制台 handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)

        # 文件 handler
        fh = logging.FileHandler(_log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.addHandler(ch)
        root.addHandler(fh)

        _initialized = True

    return logger
