import time
import io
import board
from morse_translator import MorseTranslator
from digitalio import DigitalInOut, Direction, Pull
try:
    from typing import Union, Optional
except ImportError:
    pass

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False


if is_raspberrypi():
    import RPi.GPIO as GPIO

TX_GPIO = board.D8
RX_GPIO = board.D9

HIGH = 1
LOW = 0
# unit of "morse" time in seconds
MORSE_UNIT = 0.35
# acceptable error in timing
MORSE_ERROR = 0.02

MESSAGE_MAX_SIZE = 420

class Tranciever():
    def __init__(self, tx_pin=TX_GPIO, rx_pin=RX_GPIO, **kwargs):
        """

        Args:
            tx_pin (): 
            rx_pin (): 
            **kwargs: 
        """
        self._rx_state = LOW
        self._init_pins(tx_pin, rx_pin)
        self._prev: float = time.perf_counter()
        self._now: float = time.perf_counter()
        self._send_buf: list[str] = []
        self._recieve_buf = []
        self._symbol_buf: Optional[int] = ""
        self._morse_unit = MORSE_UNIT
        self._translator = MorseTranslator()


    def _init_pins(self, tx: int, rx: int):
        self._txpin = DigitalInOut(tx)
        self._txpin.direction = Direction.OUTPUT
        self._rxpin = DigitalInOut(rx)
        self._rxpin.direction = Direction.INPUT
        self._rxpin.pull = Pull.DOWN

    def update(self) -> bool:
        while len(self._send_buf) >= 1:
            # sending mode
            # toggle gpio according to symbols
            to_send: str = self._send_buf.pop(0)

            for symbol in to_send:
                bits: str = self._translator.char_to_morse(symbol)
                for i, bit in enumerate(bits):
                    self._send_bit(bit)
                    if i != len(bits):
                        time.sleep(MORSE_UNIT)
                if symbol != " ":
                    time.sleep(MORSE_UNIT*3)
            self._send_bit(" ") # end the line with a space so we get last character
        return self._recieve()
        

    def _recieve(self) -> bool:
        current_state = self._rxpin.value
        if current_state != self._rx_state:
            bit_time = self.now - self._prev
            if current_state == HIGH:
            # bit transition
                self._decode_pulse(bit_time, flag="rising")
            else:
                self._decode_pulse(bit_time, flag="falling")
            self._rx_state = current_state
            self._prev = self.now
            return True
        return False

        
    def send(self, message: list[str]) -> None:
        self._send_buf = message

    def _send_bit(self, bit: str) -> None:
        if bit == "-":
            print("-")
            self._txpin.value = HIGH
            time.sleep(MORSE_UNIT * 3)
        if bit == ".":
            print(".")
            self._txpin.value = HIGH
            time.sleep(MORSE_UNIT)
        if bit == " ":
            self._txpin.value = LOW
            time.sleep(MORSE_UNIT * 7)

        self._txpin.value = LOW


    @property
    def now(self) -> float:
        return time.perf_counter()


    def _decode_pulse(self, pulse_time: float, error=MORSE_ERROR, **kwargs) -> None:
        min_pulse = MORSE_UNIT - error
        max_pulse = MORSE_UNIT + error
        # convert to float ms
        flag = kwargs.get("flag", "falling")
        
        if pulse_time > 12 * max_pulse:
            # it's been too long since message recieved
            self._flush_symbol(clear=True)
            print("wait")
            return
        if pulse_time > 7 * min_pulse:
            # inter-word space
            self._recieve_buf.append(" ")
            print("~")
            self._flush_symbol(clear=True)
            return
        if pulse_time > 3 * min_pulse:
            if flag == "falling":
                # dash
                self._write_symbol("-")
                print("-")
            else:
                # inter-character space
                self._flush_symbol()
                print("z")
            return
        if pulse_time < max_pulse and pulse_time > min_pulse:
            # dot
            if flag == "falling":
                print(".")
                self._write_symbol(".")

        # if none of those are true, we're still in the intra-character space?

    def _write_symbol(self, sym: str):
        self._symbol_buf += sym

    def _write_bit(self, bit: int) -> None:
        if self._symbol_buf is None:
            self._symbol_buf = 0x00 | (bit & 0xFF)
        else:
            self._symbol_buf = ((self._symbol_buf << 1) | bit & 0xFF) & 0xFF


    def _flush_symbol(self, clear: bool=False) -> None:
        """
        Flush symbol buffer
        if clear, don't write it to the message buffer
        """
        if not clear and self._symbol_buf is not None:
            self._recieve_buf.append(self._symbol_buf)
            print(self._recieve_buf)
        self._symbol_buf = ""

    def flush_rx(self) -> bytearray:
        message = self._recieve_buf.copy()
        self._recieve_buf.clear()
        return message

    @property
    def symbol_buffer(self) -> Optional[int]:
        return self._symbol_buf

    @property
    def send_buf(self) -> Optional[list[str]]:
        if len(self._send_buf) > 0:
            return self._send_buf
        else:
            return None

    @property
    def recieve_buf(self) -> str:
        pass

