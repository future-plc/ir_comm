import sys
import string
from display import Display
import tty
import termios
import time
import os
import select
import fcntl
try:
    from typing import Optional
except ImportError:
    pass
# The only valid characters are A-Z, 0-9, and space
valid_chars = string.ascii_letters + string.digits + " "


# absolute witchcraft
fd = sys.stdin.fileno()
fl = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
epoll = select.epoll()
epoll.register(fd, select.EPOLLIN)

old_settings = termios.tcgetattr(fd)
def is_data():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def get_char_stdin() -> Optional[str]:
    ch = None
    try:
        tty.setcbreak(sys.stdin.fileno())
        if is_data():
            ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def main() -> int:
    disp = Display()
    disp.clear()
    disp.text_prompt("Welcome!")
    disp.draw()
    time.sleep(1)
    disp.clear()
    try:
        while 1:
            char = get_char_stdin()
            if char is not None and char != "":
                print(char)
                if ord(char) == 0x03: # keyboard interrupt
                    disp.clear()
                    disp.text_prompt("Goodbye!")
                    time.sleep(0.5)
                    return 0
                disp.user_input(char)
                disp.draw_console()
            if disp.should_exit == 0:
                disp.clear()
                disp.text_prompt("Goodbye!")
                time.sleep(0.5)
                return 0

    except KeyboardInterrupt:
        pass

    return 0

if __name__ == "__main__":
    sys.exit(main())
