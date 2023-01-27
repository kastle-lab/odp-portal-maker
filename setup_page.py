import argparse
import glob
import re
import sys
from os import makedirs, path, unlink
from pathlib import Path
from shutil import copy2, copytree, move, rmtree

from progress.bar import Bar
from ruamel.yaml import YAML

from utils import read_file, resolve_path


def move_module(ROOT_DIR, OUT_DIR, module):
    # Makes sure these strings are a directory
    ROOT_DIR = resolve_path(ROOT_DIR)
    OUT_DIR = resolve_path(OUT_DIR)
    module = resolve_path(ROOT_DIR + module)

    if not path.exists(module):
        raise FileNotFoundError(f'Cannot find module {module}. Check the path.')

    files = glob.glob(
        '**/*.*',
        recursive=True,
        root_dir=module,
    )

    # Progress Bar
    bar = Bar('Moving modules', max=len(files),
              suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for file in files:
        # Make sure the parent folder of the file is created (ignored if exists)
        makedirs(OUT_DIR + str(Path(file).parent), exist_ok=True)

        # There are directories with a '.' in it's name
        # and this prevents any directories from being copied over
        if path.isdir(module + file):
            bar.next()
            continue

        # Copy files
        copy2(module + file, OUT_DIR + file)

        bar.next()

    bar.finish()


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

    templates = glob.glob('**/', recursive=True, root_dir=resolve_path('./template'))

    print('Copying template files...', end='')

    for template in templates:
        if not path.exists(OUT_DIR + template):
            copytree(resolve_path('./template/' + template), OUT_DIR + template)

    index_template = read_file('./template/index.md')

    dirs = glob.glob('**/', recursive=True, root_dir=OUT_DIR)
    dirs.append(path.join('/'))

    excludes = ['_layouts', 'public']

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
        nested = [d for d in nested if not d.startswith('_') or not d.startswith('.')]

        files = [str(f).replace(OUT_DIR, '').replace(directory, '') for f in files]

        for d in nested:
            # Only add 1 deep nested directory
            if d.startswith('.') or d.startswith('_') or d.count('/') >= 1:
                continue

            links += f'[{d}/](./{d}/)  \n'

        for f in files:
            links += f'[{f}](./{f})  \n'

        with open(
            resolve_path(OUT_DIR + directory) + 'index.md', 'w', encoding='utf-8'
        ) as write_f:
            write_f.write(index_template + '  \n' + links)

    print('Done!')


def import_required_files(ROOT_DIR, OUT_DIR, module):
    ROOT_DIR = resolve_path(ROOT_DIR)
    OUT_DIR = resolve_path(OUT_DIR)
    OUT_DIR = resolve_path(OUT_DIR + 'public')
    module = resolve_path(ROOT_DIR + module)

    # Gets every file
    files = glob.glob(
        '**/*.*',
        recursive=True,
        root_dir=ROOT_DIR
    )

    # Ignore any files that is not a markdown
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

        # Grabs all markdown links
        # To view how the regex works: https://regex101.com/r/oTWiTP/1
        links = re.findall(r'(?<=\]\().*?(?=\s|\))', read_file(module + file), flags=re.MULTILINE)

        for link in links:
            # https://regex101.com/r/vk2ZEy/1
            if link.endswith('.md') or not re.search(r'\.[\w]*$', link):
                continue

            req_file = link.replace('../', '')

            # normalize the path
            req_file = path.normpath(req_file)

            orig_loc = resolve_path(ROOT_DIR + req_file)

            # If file doesn't exist in the original directory
            # (which means it's a url) or the path is a directory
            # then skip over
            if not path.exists(orig_loc) or path.isdir(orig_loc):
                continue

            makedirs(OUT_DIR + str(Path(req_file).parent), exist_ok=True)

            copy2(ROOT_DIR + req_file, resolve_path(OUT_DIR + req_file))

        bar.next()

    bar.finish()


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='ODP Portal Module & Config Generator',
        usage='setup_page.py [-h help] [--force] input module output',
        description='Moves specified module from converted html and generates portal config for GitHub Pages',
    )

    argParser.add_argument(
        'input',
        help='root directory of the converted markdown files (can be relative or absolute)',
    )

    argParser.add_argument(
        'module',
        help='module to move from root directory to output directory (not a path, should be the name of the folder inside the root)'
    )

    argParser.add_argument(
        'output',
        help='output path where the page is going to end up (can be relative or absolute)'
    )

    argParser.add_argument(
        '--force',
        action='store_true',
        help='if flag is turned on, it will override everything in the output directory and if the directory doesn\'t exist, create one',
    )

    args = argParser.parse_args()

    root = args.input
    out = args.output
    module = args.module

    force = args.force
    out = resolve_path(out)

    # If the '--force' flag is enabled, it will first
    # warn the user that it will override anything in
    # the target directory. It thens check if the
    # target dir exists, and deletes everything in it
    if force:
        print(
            '\n',
            'WARNING: Force flag is on. It will override the directory if it already exists.',
            sep=''
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

        makedirs(out, exist_ok=True)

    else:
        # No force mode
        try:
            # Will raise an exception if directory already exist
            makedirs(out)
        except FileExistsError as err:
            # Intercept and give hint to the --force flag
            raise FileExistsError(f'Directory already {out} exists. Use "--force" to overwrite')

    move_module(root, out, module)
    setup_config(out)
    setup_template(out)
    import_required_files(root, out, module)
