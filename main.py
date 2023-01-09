from os import makedirs, rmdir
import time

from cleandir import cleandir
from convert import convert
from fixlinks import fixlinks
from utils import resolve_path


def main():
    start_time = time.time()
    # print(resolve_path('./out'))

    convert_time = time.time()
    convert('./example', './out')
    convert_time = time.time() - convert_time

    cleandir_time = time.time()
    cleandir('./out')
    cleandir_time = time.time() - cleandir_time

    fixlinks_time = time.time()
    fixlinks('./out')
    fixlinks_time = time.time() - fixlinks_time

    print(f'Scripts took {time.time() - start_time:.2f} seconds to run...')
    print()
    print('Breakdown:')
    print(f'Converting time: {convert_time:.2f}s')
    print(f'Cleaning Directory time: {cleandir_time:.2f}s')
    print(f'Link Fixing time: {fixlinks_time:.2f}s')


if __name__ == '__main__':
    main()
