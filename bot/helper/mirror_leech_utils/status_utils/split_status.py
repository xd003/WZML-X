from time import time

from .... import LOGGER
from ...ext_utils.status_utils import (
    get_readable_file_size,
    MirrorStatus,
    get_readable_time,
)


class SplitStatus:
    def __init__(self, listener, gid):
        self.listener = listener
        self._gid = gid
        self._start_time = time()
        self.engine = "Split"

    def gid(self):
        return self._gid

    def _speed_raw(self):
        return self.listener.split_processed / (time() - self._start_time)

    def progress(self):
        if self.listener.subsize and self.listener.split_processed:
            return round(
                self.listener.split_processed * 100 / self.listener.subsize, 2
            )
        return 0

    def speed(self):
        return f"{get_readable_file_size(self._speed_raw())}/s"

    def processed_bytes(self):
        return get_readable_file_size(self.listener.split_processed)

    def name(self):
        return self.listener.name

    def size(self):
        return get_readable_file_size(self.listener.size)

    def eta(self):
        try:
            seconds = (
                self.listener.subsize - self.listener.split_processed
            ) / self._speed_raw()
            return get_readable_time(seconds)
        except ZeroDivisionError:
            return "-"

    def status(self):
        return MirrorStatus.STATUS_SPLIT

    def task(self):
        return self

    async def cancel_task(self):
        LOGGER.info(f"Cancelling Split: {self.listener.name}")
        self.listener.is_cancelled = True
        if (
            self.listener.subproc is not None
            and self.listener.subproc.returncode is None
        ):
            try:
                self.listener.subproc.kill()
            except Exception:
                pass
        await self.listener.on_upload_error("Split stopped by user!")
