import logging
import multiprocessing

from src import secret, utils


logger = logging.getLogger('init')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [init] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z')
logging_handlers = utils.make_logging_handlers(formatter)
for handler in logging_handlers:
    logger.addHandler(handler)

# 这里必须在 logging 配置之后
import src.api.app


def process(idx0: int) -> None:
    src.api.app.start(idx0, f'worker#{idx0}')


def start_worker_api() -> list[multiprocessing.Process]:
    ps: list[multiprocessing.Process] = []
    for i in range(src.secret.N_WORKERS):
        p = multiprocessing.Process(target=process, args=(i,))
        ps.append(p)
        p.start()
    return ps


if __name__ == '__main__':
    utils.fix_zmq_asyncio_windows()
    ps: list[multiprocessing.Process] = start_worker_api()

    for p in ps:
        p.join()
