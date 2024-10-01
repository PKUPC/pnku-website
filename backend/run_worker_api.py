import logging
import multiprocessing
from typing import List

from src import utils

logger = logging.getLogger('init')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    f'[%(asctime)s] [init] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %z'
)
logging_handlers = utils.make_logging_handlers(formatter)
for handler in logging_handlers:
    logger.addHandler(handler)

import src.api.app
import src.secret


def process(idx0: int) -> None:
    src.api.app.start(idx0, f'worker#{idx0}')


if __name__ == '__main__':

    utils.fix_zmq_asyncio_windows()
    ps: List[multiprocessing.Process] = []

    for i in range(src.secret.N_WORKERS):
        p = multiprocessing.Process(target=process, args=(i,))
        ps.append(p)
        p.start()

    for p in ps:
        p.join()
