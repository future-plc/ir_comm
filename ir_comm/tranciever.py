import sys
import os
import time
from datetime import datetime as dt
from datetime import timedelta
import io
try:
    import typing
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

TX_GPIO = 8
RX_GPIO = 9

HIGH = 1
LOW = 0
# unit of "morse" time in ms
MORSE_UNIT = 200
# acceptable error in timing
MORSE_ERROR = 30

MESSAGE_MAX_SIZE = 420

class Tranciever():
    def __init__(self, tx_pin=TX_GPIO, rx_pin=RX_GPIO, **kwargs):
        self._rx_state = LOW
        self._txpin: int = tx_pin
        self._rxpin: int = rx_pin
        self._prev: float = time.perf_counter()
        self._now: float = time.perf_counter()
        self._message_buf = bytearray()
        self._symbol_buf: int = 0x00
        self._morse_unit = MORSE_UNIT

        if not kwargs.get("mock", False):
            GPIO.add_event_detect(self._rxpin, GPIO.BOTH)


    def recieve(self):
        if GPIO.event_detected(self._rxpin):
            self._rx_state = GPIO.input(self._rxpin)
            bit_time = self.now - self._prev
            self._decode_pulse(bit_time)

    @property
    def now(self) -> float:
        return time.perf_counter()

    @property
    def symbol_buffer(self) -> bytes:
        return self._symbol_buf

    def _decode_pulse(self, pulse_time: float, error=MORSE_ERROR) -> None:
        min_pulse = MORSE_UNIT - error
        max_pulse = MORSE_UNIT + error
        # convert to float ms
        
        if pulse_time > 7 * min_pulse:
            # inter-word space
            self._message_buf.append(0xFF)
            self._flush_symbol(clear=True)
        if pulse_time > 3 * min_pulse:
            # inter-character space
            self._flush_symbol(clear=True)
        if pulse_time < max_pulse and pulse_time > min_pulse:
            self._symbol_buf = ((self._symbol_buf << 1) | self._rx_state & 0xFF) & 0xFF

    def send(self, message):
        raise NotImplementedError()

    def _flush_symbol(self, clear: bool=False) -> None:
        """
        Flush symbol buffer
        if clear, don't write it to the message buffer
        """
        if not clear:
            self._message_buf.append(self._symbol_buf)
        self._symbol_buf = 0x00

    def flush_message(self) -> bytearray:
        message = self._message_buf
        self._message_buf.clear()
        return message


