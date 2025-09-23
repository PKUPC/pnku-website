import logging
import multiprocessing
import time

from run_reducer_admin import start_reducer_admin
from run_worker_api import start_worker_api
from src import utils


if __name__ == '__main__':
    utils.fix_zmq_asyncio_windows()

    try:
        reducer_process = multiprocessing.Process(target=start_reducer_admin)
        reducer_process.start()

        time.sleep(2)
        worker_processes = start_worker_api()
        process_list = [reducer_process] + worker_processes
        for process in process_list:
            process.join()

    except Exception as e:
        logging.error(f'An error occurred! Main process exited. Error details: {e}')
