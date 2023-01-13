# Libraries
import time
import glob
from os import makedirs, rmdir, path
from ruamel.yaml import YAML

# Modules
from cleandir import cleandir
from convert import convert
from fixlinks import fixlinks
from utils import resolve_path, read_file


def main():
    out = '../odp-portal-test'
    start_time = time.time()

    convert_time = time.time()
    convert('./example', out)
    convert_time = time.time() - convert_time

    cleandir_time = time.time()
    cleandir(out)
    cleandir_time = time.time() - cleandir_time

    fixlinks_time = time.time()
    fixlinks(out)
    fixlinks_time = time.time() - fixlinks_time

    config_time = time.time()
    setup_config(out)
    config_time = time.time() - config_time

    print(f'Scripts took {time.time() - start_time:.2f} seconds to run...')
    print()
    print('Breakdown:')
    print(f'Converting time: {convert_time:.2f}s')
    print(f'Cleaning Directory time: {cleandir_time:.2f}s')
    print(f'Link Fixing time: {fixlinks_time:.2f}s')
    print(f'Config Setup time: {config_time:.2f}s')


def setup_config(ROOT_DIR):
    ROOT_DIR = resolve_path(ROOT_DIR, True)

    config = read_file(ROOT_DIR + '_config.yml')

    try:
        yaml = YAML()
        parsed = yaml.load(config)
        old_collections = dict()

        if 'collections' in parsed.keys():
            old_collections = parsed.get('collections')

        # TODO: Write actual code that will output a correct config file
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

        header = "# This is a generated config. Do not mess with it unless you know what you are doing!\n\n"

        with open(ROOT_DIR + '_config.yml', 'w') as config_f:
            yaml.dump(parsed, config_f)
            # config_f.write(updated_config)

    except yaml.YAMLError as err:
        print(err)


if __name__ == '__main__':
    main()
