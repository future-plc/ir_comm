import unittest

import ir_comm.tranciever
from ir_comm.tranciever import Tranciever, is_raspberrypi
HIGH = 1
LOW = 0

def bytes_to_bin(byte_array: bytearray) -> str:
    ret = ""
    for b in byte_array:
        ret += bin(b) + " "
    return ret


class TestTranciever(unittest.TestCase):
    def setUp(self):
        self.trx = Tranciever(mock=True)
        self.morseunit = self.trx._morse_unit
        self.isrpi = is_raspberrypi()

    def test_decode_basic(self):
        self.trx._rx_state = 1
        for _ in range(8):
            self.trx._decode_pulse(self.morseunit)
        result = self.trx.symbol_buffer
        self.assertEqual(result, 0x00)
        for _ in range(8):
            self.trx._decode_pulse(self.morseunit * 3)
        result = self.trx.symbol_buffer
        self.assertEqual(result, 0xFF)

    def test_decode_bit_guard(self):
        # make sure 0-255 are only possible values for symbol buffer
        self.trx._rx_state = 1
        for _ in range(20):
            self.trx._decode_pulse(self.morseunit * 3)
        result = self.trx.symbol_buffer
        self.assertEqual(result, 0xFF)

    def test_decode_space(self):
        self.trx.flush_rx()
        self.trx._decode_pulse(self.morseunit * 7)
        result = self.trx.recieve_buf
        self.assertEqual(result, bytearray([0xFF]))

    def test_decode_oneletter(self):
        # this should make an "e"
        self.trx.flush_rx()
        self.trx._rx_state = HIGH
        self.trx._decode_pulse(self.morseunit * 3)
        written_bit = self.trx.symbol_buffer
        self.assertEqual(written_bit, 0x01)
        self.trx._rx_state = LOW
        self.trx._decode_pulse(self.morseunit*3)
        written_byte = self.trx.recieve_buf
        self.assertEqual(written_byte, bytearray([0x01]))

    def test_write_bit(self):
        self.trx._flush_symbol(clear=True)
        for _ in range(4):
            self.trx._write_bit(0)
            self.trx._write_bit(1)
        self.assertEqual(self.trx.symbol_buffer, 0x55)

    def test_decode_letters(self):
        # Give it the string "abc"
        self.trx._flush_symbol(clear=True)
        self.trx.flush_rx()
        letters = [".---", "...-", "-.-."]
        correct_bin = '0b111 0b1 0b1010 '
        for i in letters:
            for c in i:
                self.trx._rx_state = HIGH
                if c == ".":
                    self.trx._decode_pulse(self.morseunit)
                if c == "-":
                    self.trx._decode_pulse(self.morseunit*3)
            # inter-letter space
            self.trx._rx_state = LOW
            self.trx._decode_pulse(self.morseunit * 3)

        result = self.trx.flush_rx()
        result = bytes_to_bin(result)
        self.assertEqual(result, correct_bin)

    def test_flush_rx(self):
        self.trx._recieve_buf = bytearray([0xFF])
        result = self.trx.flush_rx()
        self.assertEqual(result[0], 0xFF)
        self.assertEqual(self.trx._recieve_buf, bytearray())

    def test_timer(self):
        then = self.trx.now
        now = self.trx.now
        self.assertNotEqual(then, now)
        self.assertGreater(now, then)
        self.assertIsInstance(now, float)
        
     

