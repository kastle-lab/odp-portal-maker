from cleandir import cleandir
from convert import convert
from os import makedirs, rmdir


def main():

    # makedirs('./example/temp/')
    # convert('./example', './example/temp', cleanup=True)

    print('cleandir')
    cleandir('./example/temp', './example')

    rmdir('./example/temp/')


if __name__ == '__main__':
    main()
