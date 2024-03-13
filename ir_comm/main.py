import sys
import argparse
from interface import Console, Mode

parser = argparse.ArgumentParser()
parser.add_argument("-k", "--keyboard")

def main() -> int:
    args = parser.parse_args()
    if args.keyboard:
        mode = Mode.KEYBOARD
    else:
        mode = Mode.DPAD

    console = Console(mode)
    while True:
        console.run()
    

if __name__ == "__main__":
    sys.exit(main())
