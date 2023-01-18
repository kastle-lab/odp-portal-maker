from ruamel.yaml import YAML


def setup_config(ROOT_DIR, author='ODPA', desc=None):
    ROOT_DIR = resolve_path(ROOT_DIR, True)

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
        parsed['author']['name'] = author | 'ODPA'
        if desc:
            parsed['description'] = desc

        header = "# This is a generated config. Do not mess with it unless you know what you are doing!\n\n"

        with open(ROOT_DIR + '_config.yml', 'w') as config_f:
            yaml.dump(parsed, config_f)

    except yaml.YAMLError as err:
        print(err)


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
    out = args.output

    if not root:
        raise ValueError('Missing Argument: root directory')

    if not out:
        raise ValueError('Missing Argument: output directory')

    main(root, out)
