import time
from morse_dict import morse_dict, char_dict
import string
valid_chars = list(morse_dict)
valid_morse = list(char_dict)

try:
    from typing import Union
except ImportError:
    pass

class MorseTranslator():
    def __init__(self):
        self._asciibuf = ""

    def text_to_morse(self, text: str) -> list[str]:
        result = []
        for char in text:
            char = char.lower()
            if char in valid_chars:
                result.append(morse_dict[char])
            elif char == " " or char == "\n":
                result.append(char)

        if len(result) == 0:
            return []
        if result[0] in string.whitespace and len(result) == 1:
            result = []
        return result

    def char_to_morse(self, char: str) -> str:
        char = char.lower()
        return morse_dict[char]

    def morse_to_char(self, morse: Union[list[str], str]) -> str:
        result = ""
        for sym in morse:
            if sym in valid_morse:
                result += char_dict[sym]
            elif sym == " " and len(result) > 1:
                result += sym

        return result


    def morse_to_bytes(self, morse: Union[list[str], str]) -> bytearray:
        result = bytearray(len(morse))
        for symbol in morse:
            if symbol == " ":
                result.append(0xFF)  # space character
            byte = 0x00
            for unit in symbol:
                if unit == "-":
                    byte += 1
                byte = byte << 1

            result.append(byte)

        return result


        

    
