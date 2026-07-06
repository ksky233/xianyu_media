import logging

# 配置彩色日志
class ColorizedFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # 蓝色
        'INFO': '\033[92m',   # 绿色
        'WARNING': '\033[93m', # 黄色
        'ERROR': '\033[91m',  # 红色
        'CRITICAL': '\033[91m\033[1m', # 红色加粗
        'RESET': '\033[0m'    # 重置
    }

    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, '')}{log_message}{self.COLORS['RESET']}"

# 创建并配置日志器
def get_logger(name="app"):
    # 配置日志
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # 设置格式化器
        formatter = ColorizedFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        
        # 添加处理器到日志器
        logger.addHandler(console_handler)
        logger.propagate = False
    
    return logger

# 创建默认日志器实例，可以直接导入使用
logger = get_logger()