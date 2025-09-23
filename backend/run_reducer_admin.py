import asyncio
import logging
import threading

from gevent.pywsgi import WSGIServer

from src import secret, utils


logger = logging.getLogger('init')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [init] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z')
logging_handlers = utils.make_logging_handlers(formatter)
for handler in logging_handlers:
    logger.addHandler(handler)

# 这里必须在 logging 配置之后
from src.admin.app import app
from src.logic.reducer import Reducer


def start_reducer_admin() -> None:
    reducer_started_event = threading.Event()

    def reducer_thread(loop: asyncio.AbstractEventLoop, reducer: Reducer) -> None:
        async def task() -> None:
            await reducer._before_run()
            reducer_started_event.set()
            await reducer._mainloop()
            reducer.log('critical', 'run_reducer_admin.reducer_thread', 'reducer mainloop stopped')

        t = task()
        loop.create_task(t)
        loop.run_forever()

    loop = asyncio.new_event_loop()
    reducer = Reducer('reducer')
    threading.Thread(target=reducer_thread, args=(loop, reducer), daemon=True).start()
    reducer_started_event.wait()

    app.config['reducer_loop'] = loop
    app.config['reducer_obj'] = reducer
    WSGIServer(secret.REDUCER_ADMIN_SERVER_ADDR, app, log=None).serve_forever()


if __name__ == '__main__':
    utils.fix_zmq_asyncio_windows()
    start_reducer_admin()
