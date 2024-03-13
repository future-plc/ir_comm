import busio
import math
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import os
import board

FONT_SIZE = 12
# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)


class Display():
    def __init__(self, i2c: busio.I2C=i2c):
        self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        width: int = self.oled.width
        height: int = self.oled.height
        self.image = Image.new("1", (width, height))
        self.imgbuf  = ImageDraw.Draw(self.image)
        maybe_font = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        if os.path.exists(maybe_font):
            self._font = ImageFont.truetype(maybe_font, FONT_SIZE)
        else:
            self._font = ImageFont.load_default()

        self._stdout: str = ""
        self._linelength = 17
        self._linespace = 5
        self._lineheight = math.ceil(self.oled.height / FONT_SIZE) + 7

    def draw(self) -> None:
        """ Update Display """
        print("drawcall")
        self.oled.image(self.image)
        self.oled.show()

    def clear(self) -> None:
        """ Clear display """
        self.oled.fill(0)
        self._clear_buf()
        self._stdout = ""
        self.oled.show()

    def _clear_buf(self) -> None:
        """ Clear Image Buffer """
        self.imgbuf.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)

    def text_prompt(self, prompt: str, position: tuple[float, float]=(0.0,0.0)) -> None:
        """ Write a text prompt to the buffer """
        self.imgbuf.text(position, text=prompt, font=self._font, fill=255)
        self.draw()

    def set_cursor(self, char: int=0) -> None:
        """ Place a cursor at <line><char> """
        target_char = (char * round((self.oled.width/self._linelength))) % self.oled.width
        target_line = math.floor(char / self._linelength)
        self.imgbuf.text(
                (target_char, target_line),
                text="_",
                font=self._font,
                fill=255
                )

    def write_lines(self, text: str, offset: int=0) -> None:
        numlines = math.ceil(len(text) / self._lineheight)
        for i in range(numlines):
            text_slice = text[
                    i*self._linelength :
                    (i*self._linelength) + self._linelength
                    ]

            self.imgbuf.text(
                    (0, (i * self._lineheight + 1) + offset * self._lineheight),
                    text=text_slice,
                    font=self._font,
                    fill=255
                    )

    def draw_console(self):
        self.imgbuf.text((0, 10), text=self._stdout, font=self._font, fill=255)
        self.draw()

    def user_input(self, char):
        self._stdout += char
