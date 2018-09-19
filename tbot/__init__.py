import typing
import time
import functools
from tbot import log

from . import selectable
from .selectable import acquire_lab, acquire_board, acquire_uboot, acquire_linux

__all__ = (
    "selectable",
    "acquire_lab",
    "acquire_board",
    "acquire_uboot",
    "acquire_linux",
    "testcase",
)

F = typing.TypeVar("F", bound=typing.Callable[..., typing.Any])


def testcase(tc: F) -> F:
    """
    Decorate a function to make it a testcase.

    **Example**::

        @tbot.testcase
        def foobar_testcase(x: str) -> int:
            return int(x, 16)
    """

    @functools.wraps(tc)
    def wrapped(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        log.testcase_begin(tc.__name__)
        start = time.monotonic()
        try:
            result = tc(*args, **kwargs)
        except:  # noqa: E722
            log.testcase_end(time.monotonic() - start, False)
            raise
        log.testcase_end(time.monotonic() - start)
        return result

    setattr(wrapped, "_tbot_testcase", None)
    return typing.cast(F, wrapped)


flags: typing.Set[str] = set()
configs: typing.Dict[str, str] = dict()
