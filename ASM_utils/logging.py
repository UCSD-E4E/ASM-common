'''This module provides common logging facilities
'''

import datetime as dt
import logging
import logging.handlers
from logging import LogRecord
from pathlib import Path

import tzlocal

local_timezone = tzlocal.get_localzone()
class Formatter(logging.Formatter):
    """Common Aye-Aye Sleep Monitoring Log Formatter
    """
    def __init__(self) -> None:
        super().__init__(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def converter(self, timestamp) -> dt.datetime:
        dt_timestamp = dt.datetime.fromtimestamp(timestamp, tz=local_timezone)
        return dt_timestamp

    def formatTime(self, record: LogRecord, datefmt: str=None):
        timestamp = self.converter(record.created)
        if datefmt:
            s = timestamp.strftime(datefmt)
        else:
            try:
                s = timestamp.isoformat(timespec='milliseconds')
            except TypeError:
                s = timestamp.isoformat()
        return s

def configure_logging(log_dest: Path,
                      *,
                      base_level: int = logging.DEBUG,
                      file_level: int = logging.DEBUG,
                      console_level: int = logging.WARN,
                      max_file_size: int = 5*1024*1024,
                      n_backup_files: int = 5):
    root_logger = logging.getLogger()
    # Log to root to begin
    root_logger.setLevel(level=base_level)

    log_file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dest,
        maxBytes=max_file_size,
        backupCount=n_backup_files
    )
    log_file_handler.setLevel(level=file_level)

    root_formatter = Formatter()
    log_file_handler.setFormatter(root_formatter)
    root_logger.addHandler(log_file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level=console_level)

    error_formatter = Formatter()
    console_handler.setFormatter(error_formatter)
    root_logger.addHandler(console_handler)
