import unittest
from ir_comm.morse_dict import morse_dict, char_dict
from ir_comm.morse_translator import MorseTranslator
import string
valid_chars = string.ascii_lowercase + string.digits + string.ascii_uppercase
all_chars = string.printable
morse_chars = morse_dict.values()


class TestMorse(unittest.TestCase):
    def setUp(self):
        self.mt = MorseTranslator()

    def test_text_to_morse(self):
        # text should become valid morse
        for c in valid_chars:
            morse_char = self.mt.text_to_morse(c)
            self.assertEqual(morse_char, morse_dict[c.lower()] + ";")
        
    def test_invalid_text_to_morse(self):
        for c in string.printable:
            if c.lower() not in list(morse_dict):
                result = self.mt.text_to_morse(c)
                self.assertEqual(result, "")

    def morse_to_text(self):
        # morse should become valid text
        for m in morse_chars:
            result = self.mt.morse_to_char(m)
            self.assertEqual(result, char_dict[m])

    def test_invalid_morse(self):
        invalid = "--..--..; ---..----;"
        result = self.mt.morse_to_char(invalid)
        self.assertEqual(result, "")

    def test_two_way(self):
        message = "Hello World!"
        morse = self.mt.text_to_morse(message)
        text = self.mt.morse_to_char(morse)
        self.assertEqual(message.strip(";").lower(), text)

    def test_two_way_dirty(self):
        message = "Hello; World!"
        morse = self.mt.text_to_morse(message)
        text = self.mt.morse_to_char(morse)
        self.assertEqual(message, text)

    def test_eol(self):
        pass
        # catch our custom eol character

    def test_num_words(self):
        pass
