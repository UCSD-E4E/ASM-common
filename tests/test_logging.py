'''Tests that logging output works
'''

import datetime as dt
import logging
from pathlib import Path

from ASM_utils.logging import configure_logging


def test_timestamping_timezone():
    """Tests that the timestamps generated have timezone information
    """
    log_dir = Path('.')
    log_dest = log_dir.joinpath('test.log')
    log_dest.unlink(missing_ok=True)
    configure_logging(log_dest=log_dest)
    logger = logging.getLogger('test_timestamping')
    logger.info('test_message')
    with open(log_dest, 'r', encoding='ascii') as handle:
        log_line = handle.readline()
    timestamp = log_line.split()[0]
    dt_timestamp = dt.datetime.fromisoformat(timestamp)
    assert dt_timestamp.tzinfo
