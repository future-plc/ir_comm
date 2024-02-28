import sys
import time
from argparse import ArgumentParser
from display import Display

parser = ArgumentParser()
parser.add_argument("-r", "--recieve", action="store")
parser.add_argument("-s", "--send", action="store")

def main() -> int:
    args = parser.parse_args()
    disp = Display()
    disp.clear()
    disp.text_prompt("IR Morse Communicator")
    disp.draw()
    time.sleep(3)
    disp.clear()
    disp.text_prompt("Type a Message:")
    disp.draw()
    time.sleep(4)
    if args.send:
        for i in args.send:
            disp.user_input(i)
            disp.draw_console()
            time.sleep(1)
        time.sleep(3)
        disp.clear()
        disp.text_prompt("Sending!")
        disp.draw()
        time.sleep(4)
        disp.clear()
        disp.text_prompt("Message Sent")
        disp.draw()
        time.sleep(2)
        disp.clear()
        disp.text_prompt("Type a Message:")
        disp.draw()
    if args.recieve:
        time.sleep(5)
        disp.clear()
        disp.text_prompt("Message being recieved:")
        disp.draw()
        time.sleep(0.5)
        for i in args.recieve:
            disp.user_input(i)
            disp.draw_console()
            time.sleep(0.3)

    return 0

if __name__ == "__main__":
    sys.exit(main())
