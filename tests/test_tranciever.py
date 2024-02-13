import unittest

import ir_comm.tranciever
from ir_comm.tranciever import Tranciever

class TestTranciever(unittest.TestCase):
    def setUp(self):
        self.trx = Tranciever(mock=True)
        self.morseunit = self.trx._morse_unit

    def test_decode_basic(self):
        self.trx._rx_state = 1
        for _ in range(8):
            self.trx._decode_pulse(self.morseunit)
        result = self.trx.symbol_buffer
        self.assertEqual(result, 0xFF)

    def test_decode_bit_guard(self):
        # make sure 0-255 are only possible values for symbol buffer
        self.trx._rx_state = 1
        for _ in range(20):
            self.trx._decode_pulse(self.morseunit)
        result = self.trx.symbol_buffer
        self.assertEqual(result, 0xFF)

    def test_decode_space(self):
        self.trx._decode_pulse(self.morseunit * 7)
        result = self.trx._message_buf
        self.assertEqual(result, bytearray([0xFF]))
     

