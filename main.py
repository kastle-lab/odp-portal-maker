import argparse
import glob
import time
from os import makedirs, path, rmdir

from cleandir import cleandir
from convert import convert
from fixlinks import fixlinks
from utils import read_file, resolve_path


def main(root='./legacy', out='../odp-portal-test'):
    start_time = time.time()

    convert_time = time.time()
    convert(root, out)
    convert_time = time.time() - convert_time

    cleandir_time = time.time()
    cleandir(out)
    cleandir_time = time.time() - cleandir_time

    fixlinks_time = time.time()
    fixlinks(out)
    fixlinks_time = time.time() - fixlinks_time

    print(f'Scripts took {time.time() - start_time:.2f} seconds to run...')
    print()
    print('Breakdown:')
    print(f'Converting time: {convert_time:.2f}s')
    print(f'Cleaning Directory time: {cleandir_time:.2f}s')
    print(f'Link Fixing time: {fixlinks_time:.2f}s')


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='ODP Portal Maker',
        usage='main.py [-h help] input output',
        description='Converts legacy ODP website into markdown and will clean the directory creating a sane directory tree, while also keeping the relative links, fully functioning',
        epilog='This script will run all the necessary modules for complete conversion'
    )

    argParser.add_argument(
        'input',
        help='root directory of the html files. Can be relative as long as the cwd is in the proper directory'
    )

    argParser.add_argument(
        'output',
        help='output directory. Will also be used for directory cleaning and link fixing. If directory doesn\'t exist, it will create it'
    )

    args = argParser.parse_args()

    root = args.input
    out = args.output

    main(root, out)
