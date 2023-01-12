from os import makedirs, rmdir
import time
import yaml


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

    print(f'Scripts took {time.time() - start_time:.2f} seconds to run...')
    print()
    print('Breakdown:')
    print(f'Converting time: {convert_time:.2f}s')
    print(f'Cleaning Directory time: {cleandir_time:.2f}s')
    print(f'Link Fixing time: {fixlinks_time:.2f}s')


def setup_config(ROOT_DIR):
    ROOT_DIR = resolve_path(ROOT_DIR, True)

    config = read_file(ROOT_DIR + '_config.yml')

    try:
        parsed = yaml.safe_load(config)
        old_collections = parsed['collections']

        # TODO: Write actual code that will output a correct config file
        new_collections = {
            'ODP': {
                'output': True
            }
        }

        # Dictionary union https://peps.python.org/pep-0584/
        parsed['collections'] = new_collections | old_collections

        updated_config = yaml.dump(parsed)

        header = "This is a generated config. Do not mess with it unless you know what you are doing!\n\n"

        with open(ROOT_DIR + '_config.yml', 'w') as config_f:
            config_f.write(header + updated_config)

    except yaml.YAMLError as err:
        print(err)


if __name__ == '__main__':
    setup_config('../odp-portal-test')
