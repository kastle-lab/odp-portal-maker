import argparse
import json
import re
from os import environ, path
from time import sleep

import requests
from dotenv import load_dotenv

from utils import read_file, resolve_path

load_dotenv('.env')


header = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {environ["GITHUB_API_TOKEN"]}',
    'X-Github-Api-Version': '2022-11-28'
}

api_link = 'https://api.github.com/repos/odpa/patterns-repository/issues'


def create_issues(fails):

    open_issues_for_links = []
    # Get Current list of issues
    current_issues = requests.get(api_link, headers=header)
    current_issues = current_issues.json()

    for issue in current_issues:
        if (issue['state'] != 'open'):
            continue

        data = re.findall(r'(?:Raw JSON:.*?```.*?)(.*)(?:.*?```)', issue['body'],
                          flags=re.MULTILINE | re.IGNORECASE | re.DOTALL)

        data = json.loads(data[0])

        open_issues_for_links.append(data['link'])

    # print(fails)
    for fail in fails.values():

        link, files, authors = fail.values()

        if fail in open_issues_for_links:
            continue

        linkStr = f'Link: {link}  \n'
        fileStr = 'Files Associated (with links):  \n'
        authorStr = 'Authors:  \n'

        for f in files:
            f_dir = f.replace('.md', '')
            fileStr += f'  - [{f}](https://github.com/odpa/patterns-repository/tree/master/{f_dir}/{f})  \n'

        for a in authors:
            authorStr += f'  - {a}  \n'

        rawJSON = f'Raw JSON:  \n'
        rawJSON += f'```\n{json.dumps(fail)}\n```'

        commentStr = f'{linkStr}  \n{fileStr}  \n{authorStr}  \n{rawJSON}'
        title = path.split(link)[1]

        res = requests.post(api_link, json.dumps({'title': title, 'body': commentStr}), headers=header)

        print(link, res.status_code, res.json()['message'] if res.status_code == 403 else '')
        sleep(5)


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='Link Fixer',
        usage='create_issues.py [-h help] input',
        description='takes in a `failed.json` file to create issues on github',
        epilog='Part of the ODP-Portal-Maker toolset'
    )

    argParser.add_argument(
        'input',
        nargs='*',
        default='failed.json',
        help='json file to parse to create the issues based on'
    )

    args = argParser.parse_args()
    filename = args.input[0] if type(args.input) is list else args.input

    if not filename.endswith('.json'):
        raise OSError(
            f'Invalid Argument: "{filename}" is not a json file.'
        )

    find_file = resolve_path(filename)

    fails = json.loads(read_file(filename))

    if (not path.exists(find_file)):
        raise FileNotFoundError(
            f'{filter_file} not found! Please create a filter.txt or give a valid path to a custom filter')

    create_issues(fails)
