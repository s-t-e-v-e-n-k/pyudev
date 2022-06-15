# -*- coding: utf-8 -*-
# Copyright (C) 2012 Sebastian Wiesner <lunaryorn@gmail.com>

# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.

# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
"""
    plugins.fake_monitor
    ====================

    Provide a fake :class:`~pyudev.Monitor`.

    This fake monitor allows to trigger arbitrary events.  Use this class to
    test class building upon monitor without the need to rely on real events
    generated by privileged operations.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""

# isort: STDLIB
import os
from select import select

# isort: THIRDPARTY
import pytest


class FakeMonitor(object):
    """
    A fake :class:`~pyudev.Monitor` which allows you to trigger arbitrary
    events.

    This fake monitor implements the complete :class:`~pyudev.Monitor`
    interface and works on real file descriptors so that you can
    :func:`~select.select()` the monitor.
    """

    def __init__(self, device_to_emit):
        self._event_source, self._event_sink = os.pipe()
        self.device_to_emit = device_to_emit
        self.started = False

    def trigger_event(self):
        """
        Trigger an event on clients of this monitor.
        """
        os.write(self._event_sink, b"\x01")

    def fileno(self):
        return self._event_source

    def filter_by(self, *args):
        pass

    def start(self):
        self.started = True

    def poll(self, timeout=None):
        rlist, _, _ = select([self._event_source], [], [], timeout)
        if self._event_source in rlist:
            os.read(self._event_source, 1)
            return self.device_to_emit

    def close(self):
        """
        Close sockets acquired by this monitor.
        """
        try:
            os.close(self._event_source)
        finally:
            os.close(self._event_sink)


@pytest.fixture
def fake_monitor(request):
    """
    Return a FakeMonitor, which emits the platform device as returned by
    the ``fake_monitor_device`` funcarg on all triggered actions.

    .. warning::

       To use this funcarg, you have to provide the ``fake_monitor_device``
       funcarg!
    """
    return FakeMonitor(request.getfixturevalue("fake_monitor_device"))
