import logging
import os
from datetime import datetime

class LoggerManager:
    def __init__(self, name: str, log_dir: str = "../logs"):  # 修改默认日志目录路径
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger