#!/usr/bin/env python

from mathtest import calc_postfix, \
                     in2postfix, \
                     tokenize
from test import test

def main():
    parser = test()
    parser.parseText("test.c")


if __name__ == '__main__':
    main()
