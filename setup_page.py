import glob

import argparse
import re


from progress.bar import Bar

from ruamel.yaml import YAML

from os import makedirs, path, unlink

from shutil import copy2, rmtree, move, copytree

from pathlib import Path

from utils import resolve_path, read_file


def move_module(ROOT_DIR, OUT_DIR, module):

    ROOT_DIR = resolve_path(ROOT_DIR, True)

    OUT_DIR = resolve_path(OUT_DIR, True)

    module = resolve_path(ROOT_DIR + module) + '/'

    if not path.exists(module):

        raise FileNotFoundError(f'Cannot find module {module}. Check the correctness of the path.')

    files = glob.glob(

        '**/*.*',

        recursive=True,
        root_dir=module,
    )

    bar = Bar('Moving modules', max=len(files),

              suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for file in files:

        makedirs(OUT_DIR + str(Path(file).parent), exist_ok=True)

        if path.isdir(module + file):

            bar.next()
            continue

        copy2(module + file, OUT_DIR + file)

        bar.next()

    bar.finish()


def setup_config(OUT_DIR, author='ODPA', desc=None):

    OUT_DIR = resolve_path(OUT_DIR, True)

    if not path.exists(resolve_path(OUT_DIR + '_config.yml')):

        copy2('./template/_config.yml', OUT_DIR + '_config.yml')

    config = read_file(OUT_DIR + '_config.yml')

    try:

        yaml = YAML()

        parsed = yaml.load(config)
        old_collections = dict()

        if 'collections' in parsed.keys():

            old_collections = parsed.get('collections')

        directories = glob.glob('**', root_dir=OUT_DIR)

        new_collections = dict()

        excludes = ['_includes', '_layouts', '_posts', 'css']

        for directory in directories:

            # There are some necessary folders for jekyll and we don't

            # want to include that in our output

            if directory in excludes:
                continue

            if path.isdir(OUT_DIR + directory):

                new_collections[directory] = {'output': True}

        # Dictionary union https://peps.python.org/pep-0584/

        parsed['collections'] = new_collections | old_collections

        parsed['author']['name'] = author if author else 'ODPA'

        parsed['excludes'] = ['public', '_layout']

        if desc:

            parsed['description'] = desc

        header = '# This is a generated config. Do not mess with it unless you know what you are doing!\n\n'

        with open(OUT_DIR + '_config.yml', 'w') as config_f:

            yaml.dump(parsed, config_f)

    except yaml.YAMLError as err:
        print(err)


def setup_template(OUT_DIR):

    OUT_DIR = resolve_path(OUT_DIR, True)

    templates = glob.glob('**/', recursive=True, root_dir=resolve_path('./template'))

    for template in templates:

        # if template in ['_config.yml', 'index.md']:

        # continue

        if not path.exists(OUT_DIR + template):

            # makedirs(OUT_DIR + template, exist_ok=True)

            copytree(resolve_path('./template/' + template), OUT_DIR + template)

    index_template = read_file('./template/index.md')

    dirs = glob.glob('**/', recursive=True, root_dir=OUT_DIR)

    dirs.append(path.join('/'))

    excludes = ['_layouts', 'public']

    # dirs = [path.normpath(d) for d in dirs if not d in excludes]

    for directory in dirs:

        # https://stackoverflow.com/a/8122096/13631113
        if any(map(directory.__contains__, excludes)):
            continue

        links = ''

        p = Path(OUT_DIR + directory)

        if str(p).replace(OUT_DIR, ''):

            links += '[../](../)  \n'

        nested = p.glob('*/**/')

        files = p.glob('*.*')

        nested = [


            str(n).replace(OUT_DIR, '').replace(directory, '').replace('\\', '/')
            for n in nested


        ]

        nested = [d for d in nested if not d.startswith('_') or not d.startswith('.')]

        files = [str(f).replace(OUT_DIR, '').replace(directory, '') for f in files]

        # print(list(files))

        for d in nested:

            if d.startswith('.') or d.startswith('_') or d.count('/') >= 1:
                continue

            links += f'[{d}/](./{d}/)  \n'

        for f in files:

            links += f'[{f}](./{f})  \n'

        with open(


            resolve_path(OUT_DIR + directory, True) + 'index.md', 'w', encoding='utf-8'


        ) as write_f:

            write_f.write(index_template + '  \n' + links)


def import_required_files(ROOT_DIR, OUT_DIR, module):

    ROOT_DIR = resolve_path(ROOT_DIR, True)

    OUT_DIR = resolve_path(OUT_DIR, True)

    OUT_DIR = resolve_path(OUT_DIR + 'public', True)

    module = resolve_path(ROOT_DIR + module) + '/'

    files = glob.glob(


        '**/*.*',


        recursive=True,


        root_dir=ROOT_DIR
    )

    files = [f for f in files if not f.endswith('.md')]

    out_files = glob.glob(

        '**/*.md',

        recursive=True,
        root_dir=module
    )

    bar = Bar('Importing necessary files', max=len(files),

              suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for file in out_files:

        if path.isdir(file):

            bar.next()
            continue

        # To view how the regex works: https://regex101.com/r/oTWiTP/1

        links = re.findall(r'(?<=\]\().*?(?=\s|\))', read_file(module + file), flags=re.MULTILINE)

        for link in links:

            # https://regex101.com/r/vk2ZEy/1

            if link.endswith('.md') or not re.search(r'\.[\w]*$', link):
                continue

            req_file = link.replace('../', '')

            req_file = path.normpath(req_file)

            orig_loc = resolve_path(ROOT_DIR + req_file)

            if not path.exists(orig_loc) or path.isdir(orig_loc):
                continue

            makedirs(OUT_DIR + str(Path(req_file).parent), exist_ok=True)

            copy2(ROOT_DIR + req_file, resolve_path(OUT_DIR + req_file))

        bar.next()

    bar.finish()


if __name__ == '__main__':

    argParser = argparse.ArgumentParser(

        prog='ODP Portal Config Generator',

        description='Generates Portal config for GitHub Pages',
    )

    argParser.add_argument(

        '-d',

        '-i',

        '--input',

        '--dir',

        help='root directory of the converted markdown files',
    )

    argParser.add_argument(

        '-m',

        '--module',

        help='module to move from root directory to output directory'
    )

    argParser.add_argument(

        '-o',

        '--output',

        help='output where the page is going to end up.'
    )

    argParser.add_argument(

        '--force',
        action='store_true',

        help='if flag is turned on, it will override everything in the output directory and if the directory doesn\'t exist, create one',
    )

    args = argParser.parse_args()

    root = args.input

    out = args.output

    force = args.force

    module = args.module

    if not root:

        raise ValueError('Missing Argument: root directory')

    if not out:

        raise ValueError('Missing Argument: output directory')

    if not module:

        raise ValueError('Missing Argument: module to move')

    out = resolve_path(out) + '/'

    if force:

        print(


            'WARNING: Force flag is on. It will override the directory if it already exists.'
        )

        input('Press [Enter] to continue... or Terminate process to cancel')

        if path.exists(out):

            excludes = ['.git']

            folders = glob.glob(

                '**/',

                recursive=False,
                root_dir=out,

                include_hidden=False
            )

            for folder in folders:

                rmtree(out + folder)

            files = glob.glob(

                '*.*',

                recursive=False,
                root_dir=out
            )

            for file in files:

                unlink(out + file)

    else:

        if not path.exists(out):

            raise FileNotFoundError(

                f'Cannot find the directory {out}.\nMake sure it exists, or use --force flag to automatically create it')

    move_module(root, out, module)

    setup_config(out)
    setup_template(out)

    import_required_files(root, out, module)
