from typing import Optional

from pygame import draw

from display import Display
from objects import Objet, Text
from utils import Font, color, global_manager


class ActionGuide(Objet):
    height = Font.height + Font.multiplier * 2

    def __init__(self):
        display = global_manager.get_global('display')
        super().__init__(complex(0, display.size.imag - ActionGuide.height))

        self.actions = dict()

        font = Font.load('res/font/ppaa.ppf', color.BLACK)
        self.text = Text(self.pos + complex(Font.multiplier, Font.multiplier), self.convert_actions(), font)

        self.keyboard = global_manager.get_global('keyboard')

    def convert_actions(self, dictionary: Optional[dict] = None) -> str:
        result = ''
        if dictionary is None:
            dictionary = self.actions
        for key, value in dictionary.items():
            if not key:
                result += f'{value}  '
            elif isinstance(key, str):
                result += f'{key}-{value}  '
            else:
                if self.keyboard.is_pressed(key):
                    return self.convert_actions(value)
        return result

    def set_actions(self, actions: dict):
        self.actions = actions
        self.text.set_text(self.convert_actions())

    def get_size(self) -> complex:
        return complex(global_manager.get_global('display').size.real, ActionGuide.height)

    def resize(self, screen: Display):
        self.pos = complex(self.pos.real, screen.size.imag - ActionGuide.height)
        self.text.pos = self.pos + complex(Font.multiplier, Font.multiplier)

    def render(self, screen: Display):
        draw.rect(screen.window, color.SKY_PINK, (self.pos.real, self.pos.imag, screen.size.real, ActionGuide.height))
        self.text.set_text(self.convert_actions())
        self.text.render(screen)
