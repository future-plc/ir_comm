import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import os

FONT_SIZE = 10
# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

button_pins = {
        "up": board.D17,
        "down": board.D22,
        "left": board.D27,
        "right": board.D23,
        "A": board.D5,
        "B": board.D6
        }

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

class Display():
    def __init__(self, i2c: busio.I2C=i2c):
        self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        width: int = self.oled.width
        height: int = self.oled.height
        self.image = Image.new("1", (width, height))
        self.buf  = ImageDraw.Draw(self.image)
        maybe_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        if os.path.exists(maybe_font):
            self._font = ImageFont.truetype(maybe_font, FONT_SIZE)
        else:
            self._font = ImageFont.load_default()

        self._stdout: str = ""
        self._button_enter = Button(button_pins["A"])
        self._button_exit = Button(button_pins["B"])

    def draw(self) -> None:
        """ Update Display """
        self.oled.image(self.image)
        self.oled.show()

    def clear(self) -> None:
        """ Clear display """
        self.oled.fill(0)
        self._clear_buf()
        self.oled.show()

    def _clear_buf(self) -> None:
        self.buf.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)

    def text_prompt(self, prompt: str) -> None:
        """ Write a text prompt to the buffer """
        self.buf.text((0,0), text=prompt, font=self._font, fill=255)

    def draw_console(self):
        self.text_prompt("Enter Message:")
        self.buf.text((0, 10), text=self._stdout, font=self._font, fill=255)
        self.draw()

    def user_input(self, char):
        self._stdout += char

    @property
    def should_exit(self) -> int:
        return self._button_enter.state

# Input pins:
button_A = DigitalInOut(board.D5)
button_A.direction = Direction.INPUT
button_A.pull = Pull.UP

button_B = DigitalInOut(board.D6)
button_B.direction = Direction.INPUT
button_B.pull = Pull.UP

button_L = DigitalInOut(board.D27)
button_L.direction = Direction.INPUT
button_L.pull = Pull.UP

button_R = DigitalInOut(board.D23)
button_R.direction = Direction.INPUT
button_R.pull = Pull.UP

button_U = DigitalInOut(board.D17)
button_U.direction = Direction.INPUT
button_U.pull = Pull.UP

button_D = DigitalInOut(board.D22)
button_D.direction = Direction.INPUT
button_D.pull = Pull.UP

button_C = DigitalInOut(board.D4)
button_C.direction = Direction.INPUT
button_C.pull = Pull.UP




