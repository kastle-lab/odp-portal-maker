from cleandir import cleandir
from convert import convert

def main():
    convert('./example', './md')

    cleandir('./')

if __name__ == '__main__':
    main()