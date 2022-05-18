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

parser.add_argument(
    "-p, --print-output",
    type=bool,
    help="Print the scraped data in a tabular format",
    default=False,
    dest="print_output"
)

args = parser.parse_args()

def debug(message: str, force=False):
    if args.debug == True:
        lines = message.split('\n')
        for line in lines:
            print("*** ", line)