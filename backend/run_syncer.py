import logging
import multiprocessing

from src import utils


logger = logging.getLogger('init')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [init] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z')
logging_handlers = utils.make_logging_handlers(formatter)
for handler in logging_handlers:
    logger.addHandler(handler)

# 这里必须在 logging 配置之后
import src.sync.app


def process() -> None:
    src.sync.app.start('syncer')


def start_syncer() -> multiprocessing.Process:
    p = multiprocessing.Process(target=process)
    p.start()
    return p


if __name__ == '__main__':
    utils.fix_zmq_asyncio_windows()
    p: multiprocessing.Process = start_syncer()
    p.join()
