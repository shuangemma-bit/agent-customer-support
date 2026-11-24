import logging
import os
from utils.path_tool import get_abs_path
from datetime import datetime

#日志保存的根目录
LOG_ROOT = get_abs_path("logs")

#确保日志的存在
os.makedirs(LOG_ROOT,exist_ok=True)

#日志的格式配置 error， info，debug
DEFAULT_LOGGING_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

def get_logger(
        name: str ="agent",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file = None
)-> logging.Logger:
    logger = logging.getLogger(name) #获取日志记录器，没有就创建
    logger.setLevel(logging.DEBUG) #设置日志最低级别

    #列表，存放已经绑定的日志处理器
    if logger.handlers:
        return logger

    #配置控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOGGING_FORMAT)

    logger.addHandler(console_handler)

    if not log_file:
        log_file = os.path.join(
            LOG_ROOT,
            f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        )

    #配置日志文件
    file_handler = logging.FileHandler(
        log_file,encoding='utf-8'
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOGGING_FORMAT)
    logger.addHandler(file_handler)

    return logger

logger = get_logger()

if __name__ =='__main__':
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告之日")
    logger.debug("调试日志")