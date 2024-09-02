"""
This module contains the Snowflake class which is used to generate unique IDs for each object in the database.
"""

import time
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class Snowflake:
    def __init__(self, worker_id, datacenter_id, sequence=0):
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence
        self.lock = Lock()
        self.last_timestamp = -1

    def _get_timestamp(self):
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_timestamp):
        timestamp = self._get_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._get_timestamp()
        return timestamp

    def generate(self) -> object:
        with self.lock:
            timestamp = self._get_timestamp()
            if timestamp < self.last_timestamp:
                logger.error(f"Clock is moving backwards. Rejecting requests until {self.last_timestamp}.")
                raise Exception("Clock moved backwards")
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 4095
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0
            self.last_timestamp = timestamp
            return ((timestamp - 1420070400000) << 22) | (self.datacenter_id << 17) | (self.worker_id << 12) | self.sequence



if __name__ == '__main__':
    snowflake = Snowflake(1, 1)
    for i in range(10):

        print(snowflake.generate())