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

## Sweep script

This script mainly cleans up the source directory from `._` (appledouble files) and `index.php*` (php request returns) files

Usage:

```
python sweep.py [-h help] input
```

## Main script

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

## Setup Page Script

This script is mainly use to extract a specific sub directory from the main page. For example, the patterns-repository used the `Submissions` module from the directory.

Usage:

```
setup_page.py [-h help] [--force] input module output
```

Arguments:  
| Arg | Help |
| - | - |
| input | root directory of the converted markdown files (can be relative or absolute) |
| module | module to move from root directory to output directory (not a path, should be the name of the folder inside the root) |
| output | output path where the page is going to end up (can be relative or absolute) |
| --force (optional) | if flag is turned on, it will override everything in the output directory and if the directory doesn't exist, create one |

Example:

```
python setup_page.py ./out Submissions ../patterns-repository --force
```

The example run above is the run used to create the [patterns-repository](https://github.com/odpa/patterns-repository) repo.

Here is the directory tree from the example above:

```
..
├── patterns-repository/
└── odp-portal-maker/
    ├── out/
    │   ├── odp
    │   ├── ODPA
    │   ├── ...
    │   ├── Submissions
    │   ├── User
    │   └── ...
    ├── ...
    ├── setup_page.py
    └── ...
```

It will simply finds the directory that matches the name of the module given and moves it.  
The script will also moves the necessary imports like images and pdf files by crawling through each page and parsing each links

## Running Individual Scripts

If it somehow necessary to run a specific script indivudually, here are the modules that can be run individually:

-   `convert.py`
-   `fixlinks.py`
-   `cleandir.py`

and as previously mentioned, each of them have their own help page.
