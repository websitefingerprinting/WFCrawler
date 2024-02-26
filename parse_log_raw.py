import argparse
import glob
import multiprocessing
import os
import re
from contextlib import contextmanager
from datetime import datetime
from functools import partial
from os import makedirs
from os.path import join, abspath, dirname, pardir

import numpy as np

"""This is for parsing the raw log files into a format that can be used by the model.
2024/02/23 16:21:26 [DEBUG]: [Send][34.133.255.192:443] Dummy   , 0  + 536 bytes at 16:21:26.903
2024/02/23 16:21:26 [DEBUG]: [Send][34.133.255.192:443] SigFinish, 4  + 532 bytes at 16:21:26.903
2024/02/23 16:21:26 [DEBUG]: [Rcv]  Dummy   , 0  + -536 bytes at 16:21:26.947
"""
# Define the regular expression patterns
timestamp_pattern_start = re.compile(r'^\d{4}/\d{2}/\d{2}')
timestamp_pattern_end = re.compile(r'\d{2}:\d{2}:\d{2}\.\d{3}$')
type_pattern = re.compile(r'Payload|Dummy')  # Add more types as needed
numbers_pattern = re.compile(r'(-?\d+)\s*\+\s*(-?\d+)\s*bytes')

captured_file_name = '.cell'
CELL_SIZE = 512
# CELL+ TLS HEADER + MY HEADER
MY_CELL_SIZE = CELL_SIZE + 24
isDummy = 888
isReal = 1

ParsedDir = join(abspath(join(dirname(__file__), pardir)), "AlexaCrawler/parsed")


def init_directories(path):
    # Create a results dir if it doesn't exist yet
    if not os.path.exists(path):
        makedirs(path)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Parse captured traffic.')

    parser.add_argument('dir',
                        type=str,
                        metavar='<dataset path>',
                        help='Path of dataset.')
    parser.add_argument('-u',
                        action='store_true',
                        default=False,
                        help='is monitored webpage or unmonitored? (default:is monitored, false)')
    parser.add_argument('--format',
                        type=str,
                        metavar='<parsed file suffix>',
                        default='.cell',
                        help='to save file as xx.suffix')
    parser.add_argument('--proc_num',
                        type=int,
                        metavar='<process num>',
                        default=80,
                        help='The num of parallel workers')
    # Parse arguments
    args = parser.parse_args()
    return args


def parse(src_dir, dst_dir, suffix, isunmon):
    try:
        if isunmon:
            site = src_dir.split("/")[-1].split(captured_file_name)[0]
            savefiledir = join(dst_dir, site + suffix)
        else:
            site, inst = src_dir.split("/")[-1].split(captured_file_name)[0].split("-")
            savefiledir = join(dst_dir, site + "-" + inst + suffix)
        with open(src_dir, 'r') as f:
            lines = f.readlines()

        raw_trace = []
        cum_real_bytes = 0
        cum_dummy_bytes = 0
        cum_real_cells = 0
        cum_dummy_cells = 0
        for idx, line in enumerate(lines):
            line = line.rstrip('\n')

            # Extract information using regular expressions
            type_match = type_pattern.search(line)

            if type_match:
                # we only want "payload" or "dummy"
                numbers_match = numbers_pattern.search(line)
                timestamp_match_start = timestamp_pattern_start.search(line)
                timestamp_match_end = timestamp_pattern_end.search(line)

                assert numbers_match and timestamp_match_start and timestamp_match_end

                # Process the matches
                timestamp_str = ' '.join([timestamp_match_start.group(0), timestamp_match_end.group(0)])
                timestamp = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S.%f")
                timestamp = timestamp.timestamp()

                real_bytes = int(numbers_match.group(1))
                dummy_bytes = int(numbers_match.group(2))

                assert real_bytes + dummy_bytes != 0
                assert ((real_bytes >= 0 and dummy_bytes >= 0) or (real_bytes <= 0 and dummy_bytes <= 0))
                raw_trace.append([timestamp, real_bytes, dummy_bytes])
        # the timestamp could be unordered in rare cases
        raw_trace = sorted(raw_trace, key=lambda x: x[0])
        refTime = raw_trace[0][0]
        with open(savefiledir, 'w') as f:
            for time, real, dummy in raw_trace:
                timestamp = time - refTime
                direction = np.sign(real + dummy)
                cum_real_bytes += abs(real)
                cum_dummy_bytes += abs(dummy)

                for _ in range(int(np.round(abs(real) / MY_CELL_SIZE))):
                    cum_real_cells += 1
                    f.write('{:.3f}\t{:.0f}\n'.format(timestamp, direction))
                for _ in range(int(np.round(abs(dummy) / MY_CELL_SIZE))):
                    cum_dummy_cells += 1
                    f.write('{:.3f}\t{:.0f}\n'.format(timestamp, direction * isDummy))
        # print("real:{:5d} parsed real:{:5d} dummy:{:5d} parsed dummy:{:5d}"
        #       .format(int(cum_real_bytes / MY_CELL_SIZE), cum_real_cells, int(cum_dummy_bytes / MY_CELL_SIZE),
        #               cum_dummy_cells))
    except Exception as e:
        print(e)
        print("Error in {}".format(src_dir))


@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()


if __name__ == "__main__":
    args = parse_arguments()
    suffix = args.format
    isunmon = args.u
    filename = args.dir.rstrip("/").split("/")[-1]
    savedir = join(ParsedDir, filename)
    init_directories(savedir)
    print("Parsed file in {}".format(savedir))
    filelist = glob.glob(join(args.dir, '*' + captured_file_name))

    # for f in filelist[:1]:
    #   parse(f)
    # print("Totol:{}".format(len(filelist)))
    with poolcontext(processes=args.proc_num) as pool:
        results = pool.map(partial(parse, dst_dir=savedir, suffix=suffix, isunmon=isunmon), filelist)