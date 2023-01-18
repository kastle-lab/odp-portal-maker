import glob
import argparse
from ruamel.yaml import YAML
from os import makedirs, path
from shutil import copy2
from pathlib import Path

from utils import resolve_path, read_file


def setup_config(ROOT_DIR, author='ODPA', desc=None):
    ROOT_DIR = resolve_path(ROOT_DIR, True)

    if not path.exists(resolve_path(ROOT_DIR + '_config.yml')):
        copy2('./template/_config.yml', ROOT_DIR + '_config.yml')

    config = read_file(ROOT_DIR + '_config.yml')

    try:
        yaml = YAML()
        parsed = yaml.load(config)
        old_collections = dict()

        if 'collections' in parsed.keys():
            old_collections = parsed.get('collections')

        directories = glob.glob(
            '**',
            root_dir=ROOT_DIR
        )

        new_collections = dict()
        excludes = ['_includes', '_layouts', '_posts', 'css']

        for directory in directories:
            # There are some necessary folders for jekyll and we don't
            # want to include that in our output
            if directory in excludes:
                continue

            if path.isdir(ROOT_DIR + directory):
                new_collections[directory] = {
                    'output': True
                }

        # Dictionary union https://peps.python.org/pep-0584/
        parsed['collections'] = new_collections | old_collections
        parsed['author']['name'] = author if author else 'ODPA'
        if desc:
            parsed['description'] = desc

        header = "# This is a generated config. Do not mess with it unless you know what you are doing!\n\n"

        with open(ROOT_DIR + '_config.yml', 'w') as config_f:
            yaml.dump(parsed, config_f)

    except yaml.YAMLError as err:
        print(err)


def setup_template(ROOT_DIR):
    ROOT_DIR = resolve_path(ROOT_DIR, True)

    templates = glob.glob(
        '**/*.*',
        recursive=True,
        root_dir=resolve_path('./template')
    )

    for template in templates:
        if template in ['_config.yml', 'index.md']:
            continue

        if not path.exists(ROOT_DIR + template):
            makedirs(ROOT_DIR + template, exist_ok=True)
            copy2(resolve_path('./template/' + template), ROOT_DIR + template)

    index_template = read_file('./template/index.md')

    dirs = glob.glob(
        '**/',
        recursive=True,
        root_dir=ROOT_DIR
    )

    dirs.append(path.join('/'))

    for directory in dirs:
        links = ""
        p = Path(ROOT_DIR + directory)

        if str(p).replace(ROOT_DIR, ''):
            links += '[../](../)  \n'

        nested = p.glob('*/**/')
        files = p.glob('*.*')

        nested = [str(n).replace(ROOT_DIR, '').replace(directory, '').replace('\\', '/') for n in nested]
        nested = [d for d in nested if not d.startswith('_') or not d.startswith('.')]
        files = [str(f).replace(ROOT_DIR, '').replace(directory, '') for f in files]

        # print(list(files))
        for d in nested:
            if d.startswith('.') or d.startswith('_') or d.count('/') >= 1:
                continue
            links += f'[{d}/](./{d}/)  \n'

        for f in files:
            links += f'[{f}](./{f})  \n'

        with open(resolve_path(ROOT_DIR + directory, True) + 'index.md', 'w', encoding='utf-8') as write_f:
            write_f.write(index_template + '  \n' + links)


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='ODP Portal Config Generator',
        description='Generates Portal config for GitHub Pages'
    )

    argParser.add_argument(
        '-d',
        '-i',
        '--input',
        '--dir',
        help='root directory of the files and where the config will be created'
    )

    args = argParser.parse_args()

    root = args.input

    if not root:
        raise ValueError('Missing Argument: root directory')

    setup_config(root)
    setup_template(root)
