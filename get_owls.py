import argparse
import glob
import re
import urllib.request
from os import path

import requests
from progress.bar import Bar

from utils import read_file, resolve_path


def get_owls(ROOT_DIR):
    ROOT_DIR = resolve_path(ROOT_DIR)

    files = glob.glob(
        '**/*.md',
        root_dir=ROOT_DIR,
        recursive=True,
        include_hidden=True
    )

    failed = []

    # bar = Bar('Fixing links...', max=len(files),
    #           suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for filename in files:
        file_content = read_file(ROOT_DIR + filename)

        # To view how the regex works: https://regex101.com/r/5edBVE/1
        # Same as others, but grabs only .owl links
        md_links = re.findall(r'(?<=\]\()http.*?\.owl(?=\s|\))', file_content, flags=re.MULTILINE)

        # To view regex: https://regex101.com/r/vGOPHE/1
        html_links = re.findall(r'(?<=href=\")http.+?\.owl(?=\")', file_content, flags=re.MULTILINE)

        for link in set([*md_links, *html_links]):
            if 'http' not in link:
                continue

            file_output = f'{ROOT_DIR}{path.split(filename)[0]}/{path.split(link)[1]}'
            print(link)
            try:
                response = requests.get(link)

                with open(file_output, 'wb') as f:
                    f.write(response.content)

            except Exception as e:
                print('Failed to retrieve from ' + link)
                failed.append((filename, link))

        # bar.next()

    print('Done!')
    print()
    print(f'Failed retrievals: {len(failed)}')
    for fail in failed:
        print(f'{fail[0]}: {fail[1]}')


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='Link Fixer',
        usage='get_owls.py [-h help] input',
        description='Goes through all md files, finds the owl link, and tries to get the file',
        epilog='Part of the ODP-Portal-Maker toolset'
    )

    argParser.add_argument(
        'input',
        help='root directory of the files. Can be relative as long as the cwd is in the proper directory'
    )

    args = argParser.parse_args()
    root = args.input

    get_owls(root)

    # x = 'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl'
