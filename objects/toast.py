from time import time

from pygame import draw

from display import Display
from objects import Objet, Text
from utils import color, Font, global_manager
from utils.functions import center


class Toast(Objet):
    background_color = color.WHITE
    text_color = color.BLACK
    font = Font.load('res/font/ppaa.ppf', text_color)
    padding = Font.area * 2
    duration = 3

    def __init__(self, text: str):
        super().__init__(0)
        self.text = text
        self.text_objets = [Text(0+0j, line, Toast.font) for line in self.text.split('\n')]
        self.size = complex(max(Toast.font.get_width(line) for line in text.split('\n')) + Toast.padding * 2,
                            Font.area * (self.text.count('\n')+1) + Toast.padding * 2)

        self.generated = time()

        self.resize(global_manager.get_global('display'))

    def get_size(self) -> complex:
        return self.size

    def resize(self, screen: Display):
        self.pos = center(screen.size, self.get_size())
        self_size = self.get_size()
        for i, text_objet in enumerate(self.text_objets):
            text_objet.pos = self.pos + complex(center(self_size.real, Toast.font.get_width(text_objet.text)),
                                                Toast.padding + i * Font.area)

    def tick(self):
        if time() - self.generated > Toast.duration:
            self.remove = True

    def render(self, screen: Display):
        draw.rect(screen.window, Toast.background_color, ((self.pos.real, self.pos.imag),
                                                          (self.size.real, self.size.imag)))
        for text_objet in self.text_objets:
            text_objet.render(screen)
