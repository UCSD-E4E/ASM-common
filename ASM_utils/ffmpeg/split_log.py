# usage: split_log [output_stats_file] [output_info_file]

import sys
import os
import pathlib
import argparse

def process_output():
    parser = argparse.ArgumentParser(description='Split ffmpeg log files.')
    parser.add_argument('output_stats_file', help='file path for stats file')
    parser.add_argument('output_info_file', help='file path for info file')
    args = parser.parse_args()

    pathlib.Path(os.path.dirname(args.output_stats_file)).mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.dirname(args.output_info_file)).mkdir(parents=True, exist_ok=True)

    stats_file = open(args.output_stats_file, 'ab+')
    info_file = open(args.output_info_file, 'ab+')

    line = bytearray()
    while True:
        b_in = sys.stdin.buffer.read1(1)
        line.extend(b_in)
        if b_in == b'\n' or b_in == b'\r':
            out_file = stats_file if line.decode().startswith('frame') else info_file
            out_file.write(line)
            out_file.flush()
            line = bytearray()

    stats_file.close()
    info_file.close()

if __name__ == "__main__":
    process_output()