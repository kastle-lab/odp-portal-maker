# odp-portal-maker

This repository houses 3 scripts that utilizes multiple utility modules. Some modules can be run individually in which case each of them have their own help page.

For more information about each individual scripts and modules, simply run:

```
python <script>.py -h
```

to display it's help page.

_*Note: For the examples, the regular `python` command will be used, but you will most likely use `python3` command, so generalize as needed*_

---

### Requirements

Here are the requirements to run these scripts:

-   `Python: ^3.11`
-   `markdownify: 0.11.6`
-   `progress: 1.6`
-   `ruamel.yaml: 0.17.21`
-   `beautifulsoup4: 4.11.1`

Make sure the python version satisfies the requirements, then  
You can either install these dependencies yourself, or use the provided `requirements.txt` and run:

```bash
python -m pip install -r requirements.txt
```

---

# Phase 1

## Sweep script

This script mainly cleans up the source directory from `._` (appledouble files) and `index.php*` (php request returns) files

Usage:

```
python sweep.py [-h help] input
```

## Main script (Phase 1 automated)

This is the first script to be run before running the `setup_page.py` script. The main script will crawl through the provided source directory, sanitize the input, then converts it into markdown file to the output directory provided.

Usage:

```
python main.py [-h help] input output
```

Example:

```bash
# This will use the './input/' directory as source
# and output it in the './out/' directory
# If the ./out/ directory doesn't exist, it will make one
python main.py ./input ./out
```

**_Note: Be careful, because it will override whatever is in the output directory!_**

# Phase 2

this phase will not have an automatic script, instead it will walk through step by step to get the same output.

## Move module

This is the script that will move a specific module/folder out of the output of Phase 1. Each script will have an example script to run that will output the same exact output as the patterns-repository

Arguments:  
| Arg | Help |
| - | - |
| input | root directory of the converted markdown files (can be relative or absolute) |
| module | module to move from root directory to output directory (not a path, should be the name of the folder inside the root) |
| output | output path where the page is going to end up (can be relative or absolute) |

Optionals: it is recommended to use to achieve the same output
| Arg | Help|
| - | - |
| -f, --force | if flag is turned on, it will override everything in the output directory and if the directory doesn't exist, create one |
| -x, --exclude-dir | if flag is turned on, it will ignore directories and only move files |

Example:

```bash
python move_module.py -fx out Submissions ../patterns-repository
```

the script above is the one used to make https://github.com/odpa/patterns-repository

Below is an example of the file tree that the script above was ran on

```
..
├── patterns-repository/ (it will be spread in here)
└── odp-portal-maker/
    ├── out/
    │   ├── odp
    │   ├── ODPA
    │   ├── ...
    │   ├── Submissions (it will move this entire folder)
    │   ├── User
    │   └── ...
    ├── ...
    ├── setup_page.py
    └── ...
```

## Cleanup Page

`cleanup_page.py` will use a `filter.json` to walk through the output of `move_module.py` and clean it up into directories. By default, there is a `filter.json` already in this repository that can be used and edited.

Arguments:
| Arg | Help |
| - | - |
| input | the directory that the script will cleanup (most likely where ever `move_module.py` outputs) |
| filter (optional) | by default it will use `filter.json`, but if desired, it can use a different file as filter so long as it follows the format |

Example:

```
python cleanup_page.py ../patterns-repository
```

## Resolve Imports

This script will resolve all the imports that every `.md` files in the output uses

Arguments:
| Arg | Help |
| - | - |
| directory | the directory to resolve imports to |
| source | the source directory where all the images will be located to copy |

Example:

```
python resolve_imports.py ../patterns-repository out
```

## Fixlinks

This script is also used in Phase 1, and it will do essentially the same thing in Phase 2

Arguments:
| Arg | Help |
| - | - |
| input | directory to fix links

Example:

```
python fixlinks.py ../patterns-repository
```

## Get .owl files

`get_owls.py` | this script will find all links that points to a `.owl` file and tries to fetch it.

-   It uses a 15 second timeout if a link is unresponsive.
-   It works with dropbox links as long as it is an owl file.
-   It will look through the file to make sure that the output is an owl file
-   If a fetch failed or file is not an owl file, it will dump it into `failed.json` that is used by `create_issues.py`

Arguments:
| Arg | Help |
| - | - |
| input | directory to resolve all owl files |

Example:

```
python get_owls.py ../patterns-repository
```

## Setup Page

`setup_page.py` | this script will setup the basic configuration files for GitHub Pages to run and create a static page. It will create Jekyll config files which is what GitHub Pages runs.

Arguments:
| Arg | Help |
| - | - |
| input | directory where the page is located |

Example:

```bash
python setup_page.py ../patterns-repository
```

## Create Issues

`create_issues.py` | in order to use this script, there needs to be a `.env` file containing the GitHub API key that has access to the repository.

Example `.env` file:

```
GITHUB_API_TOKEN=secret_github_api_key
```
