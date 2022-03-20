import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "-l, --limit",
    type=int,
    help="Max number of stocks to fetch; default 10000",
    default=10000,
    dest="limit"
)

parser.add_argument(
    "-d, --debug",
    type=bool,
    help="Show debug messages",
    default=True,
    dest="debug"
)

args = parser.parse_args()

def debug(message: str, force=False):
    if args.debug == True:
        print("*** ", message)