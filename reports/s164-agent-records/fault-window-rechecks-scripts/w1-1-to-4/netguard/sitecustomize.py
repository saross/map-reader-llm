"""Network guard for the fault-window re-check replays (W1-1 to W1-4).

Loaded through PYTHONPATH so that every replayed process, including its
subprocesses, refuses any internet-family socket connection: a hard
guarantee that no replay step can reach a model API. Unix-domain sockets
(used by multiprocessing) stay allowed. It does not touch any computation.
"""
import socket

_real_connect = socket.socket.connect
_real_connect_ex = socket.socket.connect_ex


def _guard(self, *args, **kwargs):
    if self.family in (socket.AF_INET, socket.AF_INET6):
        raise RuntimeError("NETWORK BLOCKED by the fault-window re-check guard")
    return _real_connect(self, *args, **kwargs)


def _guard_ex(self, *args, **kwargs):
    if self.family in (socket.AF_INET, socket.AF_INET6):
        raise RuntimeError("NETWORK BLOCKED by the fault-window re-check guard")
    return _real_connect_ex(self, *args, **kwargs)


socket.socket.connect = _guard
socket.socket.connect_ex = _guard_ex
