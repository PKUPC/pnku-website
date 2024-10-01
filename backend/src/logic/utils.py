import logging

from typing import Callable, Any

CbMethod = Callable[[Any, Any], Any] | Callable[[Any, Any, Any], Any]

logger = logging.getLogger('init')


def make_callback_decorator(caller: str = "anonymous") \
        -> tuple[Callable[[Any], Callable[[CbMethod], CbMethod]], dict[Any, CbMethod]]:
    listeners: dict[Any, CbMethod] = {}

    # decorator 接受一个 glitter 中定义的某种名称，返回一个装饰器
    # wrapper 是实际作用在函数上的装饰器，会将这个函数注册到 listeners 中，并返回原来的函数
    def decorator(event_name: Any) -> Callable[[CbMethod], CbMethod]:
        def wrapper(fn: CbMethod) -> CbMethod:
            if fn is not listeners.get(event_name, fn):
                raise RuntimeError(f'[{caller}] event listener already registered: {event_name}')

            listeners[event_name] = fn
            logger.info(f'[{caller}] registered event listener: {event_name}')
            return fn

        return wrapper

    return decorator, listeners
