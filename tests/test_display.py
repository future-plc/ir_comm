import unittest
from ir_comm.display import Display
from test_tranciever import is_raspberrypi

raspi_flag = is_raspberrypi()

class TestDisplay(unittest.TestCase):
    def setUp(self):
        self.disp = Display()

    def test_display(self):
        pass

