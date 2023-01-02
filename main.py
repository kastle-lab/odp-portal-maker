from cleandir import cleandir
from convert import convert
from os import makedirs, rmdir


def main():

    convert('./example', './out')

    cleandir('./out')



if __name__ == '__main__':
    main()
