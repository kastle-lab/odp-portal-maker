import argparse
import glob
import re
import urllib.request
from os import path
from shutil import copy2

import requests
from progress.bar import Bar

from utils import read_file, resolve_path


def get_owls(ROOT_DIR):
    ROOT_DIR = resolve_path(ROOT_DIR)

    # We are using fake chrome browser agent header to trick some links that blocks non-browser requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
    }
    timeout = 5

    files = glob.glob(
        '**/*.md',
        root_dir=ROOT_DIR,
        recursive=True,
        include_hidden=True
    )

    failed = {}
    cache = {}

    bar = Bar('Resolving Links', max=len(files), suffix='%(percent).1f%% - [0] %(elapsed)ds')
    bar.count = 0

    for filename in files:
        file_content = read_file(ROOT_DIR + filename)
        tail = path.split(filename)[1]

        # To view how the regex works: https://regex101.com/r/NvpkJM/3
        # Same as others, but grabs only .owl links
        links = re.findall(r'(?:(?<=\]\()|(?<=href=\"))[^\"\)\]]+?\.owl', file_content, flags=re.MULTILINE)
        links = set(links)

        for _i, link in enumerate(links):
            if 'http' not in link:
                continue
            
            bar.count += 1
            bar.message = f'Resolving {_i + 1}/{len(links)} in {tail if len(tail) < 15 else "current file"}'
            bar.suffix = f'%(percent).1f%% - [{bar.count}] %(elapsed)ds'

            link = re.sub(r'http.+ClickHandler&link=', '', link)
            file_output = f'{ROOT_DIR}{path.split(filename)[0]}/{path.split(link)[1]}'

            # This flag is created solely to avoid code duplication
            # for the exception handling
            excepted = True

            try:
                # Use a 15 sec timeout
                response = requests.get(link, timeout=timeout)

                # This gets the end url (useful when there is redirects)
                end_url = response.url

                # if returned forbidden, try requesting with browser agent headers
                if response.status_code == 403:
                    response = requests.get(link, headers=headers, timeout=timeout)

                # If it's a dropbox link and it's an owl file,
                # send a dl=1 query | meaning it will download the file
                if 'dropbox.com' in end_url and end_url.endswith('.owl'):
                    response = requests.get(end_url + '?dl=1', timeout=timeout)

                # This is the best way to check if it's an owl file
                # for now (maybe it is the best?)
                if not any(map(str(response.content).__contains__, ['http://www.w3.org/2002/07/owl', 'owl'])):
                    raise Exception()
                
                if cache.get(link):
                    copy2(cache.get(link), file_output)
                    excepted = False
                    continue

                with open(file_output, 'wb') as f:
                    f.write(response.content)
                    cache[link] = file_output

                excepted = False

            except requests.exceptions.Timeout as e:
                continue
            except Exception as e:
                continue

            finally:
                if not excepted:
                    continue

                if failed.get(link):
                    failed[link].append(filename)
                else:
                    failed[link] = [filename]
        bar.next()

    bar.finish()

    print('Done!')
    print()
    print(f'Failed retrievals: {len(failed)}')
    for fail in failed.keys():
        print(f'{fail}')


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
