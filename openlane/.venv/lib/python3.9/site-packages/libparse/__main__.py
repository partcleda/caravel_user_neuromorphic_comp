
import sys
import json
from argparse import ArgumentParser

from . import LibertyParser, __version__

def main(argv):
    p = ArgumentParser("libparse")
    p.add_argument("-v", "--version", action='version', version=f'%(prog)s {__version__}')
    p.add_argument("file", nargs=1)
    ns = p.parse_args(argv)
    f = open(ns.file[0], "r")
    try:
        parsed = LibertyParser(f)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(1)
    print(json.dumps(parsed.ast.to_dict()))

if __name__ == "__main__":
    main(sys.argv[1:])
