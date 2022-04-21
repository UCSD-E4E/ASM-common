# usage: split_log [output_stats_file] [output_info_file]

import argparse
import os
import pathlib
import sys


def process_output():
    parser = argparse.ArgumentParser(description='Split ffmpeg log files.')
    parser.add_argument('output_stats_file', help='file path for stats file')
    parser.add_argument('output_info_file', help='file path for info file')
    args = parser.parse_args()

    stats_dir = os.path.dirname(args.output_stats_file)
    info_dir = os.path.dirname(args.output_info_file)
    pathlib.Path(stats_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(info_dir).mkdir(parents=True, exist_ok=True)

    stats_file = open(args.output_stats_file, 'ab+')
    info_file = open(args.output_info_file, 'ab+')

    line = bytearray()
    while True:
        # read1 to prevent excess read calls/blocking
        b_in = sys.stdin.buffer.read1(1)
        line.extend(b_in)
        if b_in == b'\n' or b_in == b'\r':
            is_frame = line.decode().startswith('frame')
            out_file = stats_file if is_frame else info_file
            out_file.write(line)
            out_file.flush()
            line = bytearray()

if __name__ == "__main__":
    process_output()
