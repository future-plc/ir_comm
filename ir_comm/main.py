import sys
import string
from interface import Console, Mode
try:
    from typing import Optional
except ImportError:
    pass
# The only valid characters are A-Z, 0-9, and space
valid_chars = string.ascii_letters + string.digits + " "



def main() -> int:
    console = Console(Mode.DPAD)
    while True:
        console.run()
    
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
