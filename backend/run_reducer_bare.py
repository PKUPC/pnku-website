import asyncio

from src import utils
from src.logic.reducer import Reducer

if __name__ == '__main__':
    utils.fix_zmq_asyncio_windows()
    reducer = Reducer('reducer')
    asyncio.run(reducer.run_forever())
