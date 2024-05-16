import logging
import pkgutil
from functools import wraps
from importlib import import_module
from pprint import pformat
from typing import Any, Callable, Coroutine

import blinker

from jg.hen.models import Insight, Outcome


on_profile = blinker.Signal()
on_avatar_response = blinker.Signal()
on_social_accounts = blinker.Signal()
on_repo = blinker.Signal()
on_repos = blinker.Signal()


logger = logging.getLogger("jg.hen.signals")


def load_receivers(package_import_paths: list[str]):
    for package_import_path in package_import_paths:
        import_package(package_import_path)
    for name, signal in get_signals().items():
        receivers = get_receivers(signal)
        logger.debug(
            f"Signal {name!r} has {len(receivers)} receiver(s):\n{pformat(list(receivers.keys()))}"
        )


def import_package(package_import_path: str):
    logger.debug(f"Importing {package_import_path}")
    package = import_module(package_import_path)
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__):
        module_import_path = f"{package_import_path}.{module_name}"
        logger.debug(f"Importing {module_import_path}")
        import_module(module_import_path)


def get_signals() -> dict[str, blinker.Signal]:
    return {
        name: value
        for name, value in globals().items()
        if name.startswith("on_") and isinstance(globals()[name], blinker.Signal)
    }


def get_receivers(signal: blinker.Signal) -> dict[str, Any]:
    receivers = [receiver() for receiver in signal.receivers.values()]
    return {
        f"{receiver.__module__}.{receiver.__qualname__}": receiver
        for receiver in receivers
    }


async def send(signal: blinker.Signal, **kwargs) -> list[Outcome | Insight]:
    return collect_results(await signal.send_async(None, **kwargs))


def collect_results(
    raw_results: list[tuple[Callable, Outcome | Insight | None]],
) -> list[Outcome | Insight]:
    return [result for _, result in raw_results if result]


def rule(signal: blinker.Signal, docs_url: str) -> Callable:
    def decorator(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        @wraps(fn)
        async def wrapper(sender: None, *args, **kwargs) -> Outcome | None:
            try:
                result = await fn(*args, **kwargs)
                if result is not None:
                    return Outcome(
                        rule=fn.__name__,
                        status=result[0],
                        message=result[1],
                        docs_url=docs_url,
                    )
                logger.debug(f"Rule {fn.__name__!r} returned no outcome")
            except NotImplementedError:
                logger.warning(f"Rule {fn.__name__!r} not implemented")
            return None

        signal.connect(wrapper)
        return wrapper

    return decorator


def insight(signal: blinker.Signal) -> Callable:
    def decorator(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        @wraps(fn)
        async def wrapper(sender: None, *args, **kwargs) -> Insight:
            try:
                value = await fn(*args, **kwargs)
                if value is None:
                    logger.debug(f"Insight {fn.__name__!r} returned no value")
            except NotImplementedError:
                logger.warning(f"Insight {fn.__name__!r} not implemented")
            return Insight(name=fn.__name__, value=value)

        signal.connect(wrapper)
        return wrapper

    return decorator
