import tty
import termios
import select
import sys
import board
import time
import logging
from digitalio import DigitalInOut, Direction, Pull
from enum import Enum
from display import Display 
from tranciever import Tranciever
from typing import Optional
from string import ascii_uppercase, digits

# maximum printable position at current font size
MAX_CURSOR = 128

dpad_pins = {
        "up": board.D17,
        "down": board.D22,
        "left": board.D27,
        "right": board.D23,
        }
button_pins = {
        "A": board.D5,
        "B": board.D6
        }
class Mode(Enum):
    KEYBOARD = 1
    DPAD = 2

class Dpad(Enum):
    VOID = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    CLICK = 5

class Button():
    def __init__(self, pin: int, name: str=""):
        self._dio = DigitalInOut(pin)
        self._dio.direction = Direction.INPUT
        self._dio.pull = Pull.UP
        self._name = name

    @property
    def state(self) -> int:
        return self._dio.value

    @property
    def name(self) -> str:
        return self._name

class DpadButton(Button):
    def __init__(self, pin:int, cardinal:Dpad, name:str=""):
        super().__init__(pin, name)
        self._cardinal = cardinal

    @property
    def direction(self) -> Dpad:
        if not self.state:
            return self._cardinal
        else:
            return Dpad.VOID

class Console():
    def __init__(self, mode: Mode=Mode.KEYBOARD):
        self._stdin = StdInReader()
        self._disp = Display()
        self._trx = Tranciever()
        self._mode = mode
        self._dpad: list[DpadButton] = self._init_dpad()
        self._send_button = Button(board.D5)
        self._clear_send_button = Button(board.D6)
        self._disp.clear()
        # list of possible accepted symbols
        self._symbols: str = ascii_uppercase + digits + " "
        # buffer to store the message to be sent
        self._send_buf: list[str] = []
        # keeps track of the cursor position
        self._cursor = 0
        # keeps track of characters by dict index
        self._char_idxs: list[int] = [0]
    

    def run(self) -> None:
        """ Main loop of console """
        if self._mode == Mode.KEYBOARD:
            char = self._stdin.get()
            if char is not None and char != "":
                self._setchar(char)
                self._cursor += 1

        if self._mode == Mode.DPAD:
            if self._setcursor():
                self._setchar()
                self._update_display()
            if self._send_button.state == 0:
                self.write_send()

        if self._clear_send_button.state == 0:
            self._flush()
            self._disp.clear()

        if self._trx.update():
            # currently recieving a message
            msg = self._trx.get_message()
            if msg is not None:
                self._disp.write_lines(msg, 4)

    def write_send(self) -> None:
        """Send message using tranciever member"""
        self._disp.clear()
        self._disp.write_lines("Sending Message!")
        self._disp.draw()
        self._trx.send(self._send_buf)
        self._flush()
        time.sleep(0.5)
        self._disp.clear()
        self._disp.write_lines("Message sent!")
        self._disp.draw()

    def _flush(self):
        """Clear buffer and reset cursor"""
        self._send_buf = []
        self._char_idxs = [0]
        self._cursor = 0


    def _setcursor(self) -> bool:
        """Set the position of the cursor and select characters"""
        dir = self.read_dpad()
        if dir == Dpad.LEFT and self._cursor > 0:
            # cursor left
            print("left")
            self._cursor -= 1
        if dir == Dpad.RIGHT and self._cursor < MAX_CURSOR:
            print("right")
            # cursor right
            self._cursor += 1
            if self._cursor >= len(self._char_idxs):
                self._char_idxs.append(0)
        if dir == Dpad.UP:
            print("up")
            # character up
            self._char_idxs[self._cursor] += 1
        if dir == Dpad.DOWN:
            print("down")
            # character down
            self._char_idxs[self._cursor] -= 1
        if dir != Dpad.VOID:
            return True
        return False

    def _setchar(self, char: Optional[str]=None) -> None:
        """Convert char index to actual symbols"""
        if char:
            self._send_buf.append(char)
        self._send_buf = [self._symbols[i] for i in self._char_idxs]

        
    def _update_display(self):
        text = ''.join(self._send_buf)
        self._disp.clear()
        self._disp.set_cursor(self._cursor)
        self._disp.write_lines(text)
        self._disp.draw()

    def read_dpad(self) -> Dpad:
        """Check Dpad buttons, return state of any active ones"""
        for i in self._dpad:
            # if button LOW, return that state
            if i.direction != Dpad.VOID:
                return i.direction
        return Dpad.VOID

    def _init_dpad(self) -> list[DpadButton]:
        """Initialize Dpad button array"""
        dpad = []
        directions = [Dpad.UP, Dpad.DOWN, Dpad.LEFT, Dpad.RIGHT]
        i = 0
        for k, v in dpad_pins.items():
            dpad.append(DpadButton(pin=v, cardinal=directions[i], name=k))
            i += 1
        return dpad
    



class StdInReader():
    """ This changes terminal modes and gets keypresses one by one from stdin """
    def __init__(self):
        self._fd = sys.stdin.fileno()
        self._old_settings = termios.tcgetattr(self._fd)
        pass

    def get(self) -> Optional[str]:
        return self._get_char_stdin()
        
    def _get_char_stdin(self) -> Optional[str]:
        ch = None
        try:
            tty.setcbreak(sys.stdin.fileno())
            if self._is_data():
                ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)
            return ch

    def _is_data(self):
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
