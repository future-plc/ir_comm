import time
from ir_comm.morse_dict import morse_dict, char_dict
import string
valid_chars = string.ascii_lowercase + string.digits + "\n"
valid_morse = list(char_dict).append(";", " ")

DELIMITER = ";"
class MorseString():
    def __init__(self, string: str) -> None:
        self._string = string

    def
class MorseTranslator():
    def __init__(self):
        self._asciibuf = ""
        pass

    def text_to_morse(self, text: str) -> str:
        result = ""
        for char in text:
            char = char.lower()
            if char not in valid_chars:
                break
            if char == "\n":
                return result
            if char == " ":
                result += char + DELIMITER
            result += morse_dict[char] + DELIMITER
        return result

    def morse_to_char(self, morse: str) -> str:
        result = ""
        morse_symbols = morse.split(DELIMITER)  
        print(morse_symbols)
        for sym in morse_symbols:
            if sym == " ":
                result += sym
            elif sym in valid_morse:
                result += char_dict[sym]

        return result

    def split_morse(self, morse: str) -> str

    
