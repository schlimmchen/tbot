# tbot, Embedded Automation Tool
# Copyright (C) 2019  Harald Seiler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import abc
import contextlib
import typing

from .. import channel, linux
from . import connector

SelfSubprocess = typing.TypeVar("SelfSubprocess", bound="SubprocessConnector")


class SubprocessConnector(connector.Connector):
    """
    Connector using a subprocess shell.

    Arguably the simplest connector; simply spawns a subprocess with a shell.
    This is the connector used by the default local lab-host.

    **Example**:

    .. code-block:: python

        from tbot.machine import connector, linux

        class MyMachine(
            connector.SubprocessConnector,
            linux.Bash,
        ):
            pass

        with MyMachine() as localhost:
            localhost.exec0("echo", "Hello!")
    """

    __slots__ = ()

    def _connect(self) -> channel.Channel:
        return channel.SubprocessChannel()

    def clone(self: SelfSubprocess) -> SelfSubprocess:
        """Clone this machine."""
        return type(self)()


SelfConsole = typing.TypeVar("SelfConsole", bound="ConsoleConnector")


class ConsoleConnector(connector.Connector):
    """
    Connector for serial-consoles.

    As this can work in many different ways, this connector is intentionally as
    generic as possible.  To configure a serial connection, you need to
    implement the :py:meth:`ConsoleConnector.connect` method.  That methods
    gets a lab-host channel which it should transform into a channel connected
    to the board's serial console.

    **Example**:

    .. code-block:: python

        import tbot
        from tbot.machine import board, connector

        class MyBoard(
            connector.ConsoleConnector,
            board.Board,
        ):
            def connect(self, mach):
                return mach.open_channel("picocom", "-b", "115200", "/dev/ttyACM0")

        with tbot.acquire_local() as lo:
            with MyBoard(lo) as b:
                ...
    """

    @abc.abstractmethod
    def connect(self, mach: linux.LinuxShell) -> typing.ContextManager[channel.Channel]:
        """
        Connect a machine to the serial console.

        Overwrite this method with the necessary logic to connect the given
        machine ``mach`` to a channel connected to the board's serial console.

        In most cases you'll accomplish this using
        :py:meth:`mach.open_channel(...) <tbot.machine.linux.LinuxShell.open_channel>`.
        """
        raise NotImplementedError("abstract method")

    def __init__(self, mach: linux.LinuxShell) -> None:
        """
        :param LinuxShell mach: A cloneable lab-host machine.  The
            :py:class:`ConsoleConnector` will try to clone this machine's
            connection and use that to connect to the board.  This means that
            you have to make sure you give the correct lab-host for your
            respecitive board to the constructor here.
        """
        self.host = mach

    @contextlib.contextmanager
    def _connect(self) -> typing.Iterator[channel.Channel]:
        with self.host.clone() as cloned, self.connect(cloned) as ch:
            yield ch
            # yield cloned.open_channel("picocom", "-b", str(115200), "/dev/ttyUSB0")

    def clone(self: SelfConsole) -> SelfConsole:
        """This machine is **not** cloneable."""
        raise NotImplementedError("can't clone a serial connection")
