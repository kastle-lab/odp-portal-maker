import argparse
import glob
from os import path
from pathlib import Path
from shutil import copy2, copytree

from ruamel.yaml import YAML

from utils import read_file, resolve_path


def setup_config(OUT_DIR, author='ODPA', desc=None):
    OUT_DIR = resolve_path(OUT_DIR)

    # ensures config file exists
    if not path.exists(resolve_path(OUT_DIR + '_config.yml')):
        copy2('./template/_config.yml', OUT_DIR + '_config.yml')

    config = read_file(OUT_DIR + '_config.yml')

    print('Setting up config files...', end='')

    # Start setting up the config file
    yaml = YAML()

    parsed = yaml.load(config)
    old_collections = dict()

    # Get collections which is how Jekyll knows to create
    # a path to render in the web
    # For Ex:
    # if Airline is inside collections that means
    # there will be a link for
    # https://odpa.github.io/patterns-repository/Airline/
    if 'collections' in parsed.keys():
        old_collections = parsed.get('collections')

    directories = glob.glob('**', root_dir=OUT_DIR)

    new_collections = dict()

    # There are some necessary folders for jekyll and we don't
    # want to include that in our output
    # using set to subtract items inside excludes from directories
    excludes = set(['_includes', '_layouts', '_posts', 'css'])
    directories = list(set(directories) - excludes)

    for directory in directories:
        if path.isdir(OUT_DIR + directory):
            new_collections.update({
                directory: {
                    'output': True
                }
            })

    # Dictionary union https://peps.python.org/pep-0584/
    parsed['collections'] = new_collections | old_collections
    parsed['author']['name'] = author if author else 'ODPA'
    parsed['excludes'] = ['public', '_layout']

    # If there is a new description specified
    # add it into the config
    if desc:
        parsed['description'] = desc

    # A friendly reminder
    header = '# This is a generated config. Do not mess with it unless you know what you are doing!\n\n'

    # Dump it into file stream
    with open(OUT_DIR + '_config.yml', 'w') as config_f:
        yaml.dump(parsed, config_f)

    print('Done!')


def setup_template(OUT_DIR):
    OUT_DIR = resolve_path(OUT_DIR)

    templates = glob.glob('**/', recursive=True, root_dir=resolve_path('./template'), include_hidden=False)

    print('Copying template files...', end='')

    for template in templates:
        if not path.exists(OUT_DIR + template):
            copytree(resolve_path('./template/' + template), OUT_DIR + template)

    index_template = read_file('./template/index.md')

    dirs = glob.glob('**/', recursive=True, root_dir=OUT_DIR, include_hidden=False)
    dirs.append(path.join('/'))

    excludes = ['_layouts', 'public', '.git']

    for directory in dirs:

        # https://stackoverflow.com/a/8122096/13631113
        if any(map(directory.__contains__, excludes)):
            continue

        links = ''

        # Converts the string into a directory-like string
        p = Path(OUT_DIR + directory)

        if str(p).replace(OUT_DIR, ''):
            links += '[../](../)  \n'

        nested = p.glob('*/**/')

        files = p.glob('*.*')

        # handles nested links
        # removes the root of the out directory
        nested = [
            str(n).replace(OUT_DIR, '').replace(directory, '').replace('\\', '/')
            for n in nested
        ]

        # weed out hidden files and config files
        nested = [d for d in nested if not d.startswith('_') and not d.startswith('.')]

        files = [str(f).replace(OUT_DIR, '').replace(directory, '') for f in files]

        for d in nested:
            # Only add 1 deep nested directory
            if d.startswith('.') or d.startswith('_') or d.count('/') >= 1:
                continue

            links += f'[{d}/](./{d}/)  \n'

        for f in files:
            if f.startswith('.') or f.startswith('_'):
                continue
            
            links += f'[{f}](./{f})  \n'

        with open(
            resolve_path(OUT_DIR + directory) + 'index.md', 'w', encoding='utf-8'
        ) as write_f:
            write_f.write(index_template + '  \n' + links)

    print('Done!')


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='ODP Portal Config Generator',
        usage='setup_page.py [-h help] input',
        description='Generates portal config for GitHub Pages',
    )

    argParser.add_argument(
        'input',
        help='root directory of the converted markdown files (can be relative or absolute)',
    )

    args = argParser.parse_args()

    root = args.input

    setup_config(root)
    setup_template(root)
