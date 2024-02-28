import tty
import termios
import select
import sys
import board
from digitalio import DigitalInOut, Direction, Pull
from enum import Enum
from display import Display 
from tranciever import Tranciever
from typing import Optional, Never
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
        # needs direct access to buttons!
        self._mode = mode
        self._dpad: list[DpadButton] = self._init_dpad()
        self._send_button = Button(board.D5)
        self._exit_button = Button(board.D6)
        self._disp.clear()
        self._symbols: str = ascii_uppercase + digits + " "
        self._send_buf: list[str] = []
        self._cursor = 0
        # self._char_index = 0
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
        self._trx.update()

    def write_send(self) -> None:
        self._trx.send(self._send_buf)

    def _setcursor(self) -> bool:
        dir = self.read_dpad()
        if dir == Dpad.LEFT and self._cursor > 0:
            # cursor left
            print("left")
            self._cursor -= 1
        if dir == Dpad.RIGHT and self._cursor < MAX_CURSOR:
            print("right")
            # cursor right
            self._cursor += 1
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
        if self._char_index > len(self._symbols) - 1:
            self._char_index = 0

        if self._char_index < 0:
            self._char_index = len(self._symbols) - 1

        if char:
            current_char = char

        else:
            current_char = self._symbols[self._char_index]

        if self._cursor + 1 > len(self._send_buf):
            self._send_buf.append(current_char)
        else:
            self._send_buf[self._cursor] = current_char

        

    def _update_display(self):
        text = ''.join(self._send_buf)
        self._disp.clear()
        self._disp.write_lines(text)
        self._disp.draw()

    def read_dpad(self) -> Dpad:
        for i in self._dpad:
            if i.direction != Dpad.VOID:
                return i.direction
        return Dpad.VOID

    def _init_dpad(self) -> list[DpadButton]:
        dpad = []
        directions = [Dpad.UP, Dpad.DOWN, Dpad.LEFT, Dpad.RIGHT]
        i = 0
        for k, v in dpad_pins.items():
            dpad.append(DpadButton(pin=v, cardinal=directions[i], name=k))
            i += 1
        return dpad
    



class StdInReader():
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
