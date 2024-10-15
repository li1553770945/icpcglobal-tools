import logging
from logging.handlers import RotatingFileHandler
import os
def setup_logger():
    # 日志文件路径
    log_file_path = 'app.log'

    # 设置日志级别
    log_level = logging.DEBUG

    # 创建一个日志器
    logger = logging.getLogger('MyLogger')
    logger.setLevel(log_level)

    # 定义日志格式
    log_format = '%(filename)s:%(lineno)d-%(asctime)s-【%(levelname)s】：%(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # 文件处理器，设置编码为 UTF-8
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10485760, backupCount=5, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

    # 清除已有的处理器
    if logger.hasHandlers():
        logger.handlers.clear()

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

if __name__ == '__main__':
    logger = setup_logger()
    # 记录一些日志
    logger.debug('这是一个 debug 级别的消息')
    logger.info('这是一个 info 级别的消息')
    logger.warning('这是一个 warning 级别的消息')
    logger.error('这是一个 error 级别的消息')
    logger.critical('这是一个 critical 级别的消息')
