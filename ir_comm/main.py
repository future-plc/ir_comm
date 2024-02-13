import time
import struct
import string

# The only valid characters are A-Z, 0-9, and space
valid_chars = string.ascii_letters + string.digits + " "
class Morse:

    def __init__(self):
        # a dictionary formatted like "<ASCII_CHAR>": morse_byte
        self._lookup_table = None
        pass

    def encode(self, message: str) -> str:
        for char in message:
             morse_char = self._lookup_table[char]

    def decode(self, message: str) -> str:
        pass


class Tranciever:
    def __init__(self):
        self._rx_buffer: list[str] = []
        self.timer = Timer()
        self.ir_state
        self.prev_ir_state
        pass

    def send(self, packet):
        for p in packet:
            if p == ".":
                pass  # send dot
            if p == "-":
                pass  # send dash
            if p == " ":
                pass  # send space

    def recieve(self) -> None:
        now = self.timer.now


        self.timer.tick()

        

morse_dict = {
        "a" = ".-"
        "b" = "-..."
        "c" = "-.-."
        "d" = "-.."
        "e" = "."
        }
if __name__ == "__main__":
    pass
