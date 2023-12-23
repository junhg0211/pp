from display import Display
from objects import Objet
from utils import Font


class Text(Objet):
    def __init__(self, pos: complex, text: str, font: Font):
        super().__init__(pos)
        self.text = text
        self.font = font

        self.surface = None
        self.set_text(self.text)

    def get_size(self) -> complex:
        return complex(self.surface.get_width(), self.surface.get_height())

    def render(self, screen: Display):
        screen.window.blit(self.surface, (self.pos.real, self.pos.imag))

    def resize(self, screen: Display):
        pass

    def set_text(self, text: str):
        self.text = text
        self.surface = self.font.render(self.text)
