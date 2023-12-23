from random import choice

from pygame.constants import K_x, K_LSHIFT, K_e, K_f

from display import Display
from objects import Text
from state import State
from utils import Font, color, global_manager


class Initial(State):
    def __init__(self):
        font = Font.load("res/font/ppaa.ppf", color.WHITE)
        self.text = Text(0, "pp", font).center(diff=-Font.height * 1j)
        self.quote = Text(0, self.get_quote(), font).center(diff=Font.height * 1j)
        self.display = global_manager.get_global('display')

        global_manager.get_global('action_guide').set_actions({
            '': '&)',
            'c': 'change quote',
            K_LSHIFT: {
                '': '&',
                'e': 'edit',
                'f': 'files',
                'x': 'exit',
            }
        })

        self.keyboard = global_manager.get_global('keyboard')

    def get_quote(self) -> str:
        with open('res/quotes.txt', 'r') as f:
            return choice(f.readlines()).rstrip()

    def tick(self):
        if self.keyboard.is_pressed(K_LSHIFT):
            self.keyboard.is_down(K_x) and global_manager.set_global('state', ('exit',))
            self.keyboard.is_down(K_e) and global_manager.set_global('state', ('new',))
            self.keyboard.is_down(K_f) and global_manager.set_global('state', ('files',))
        else:
            buffer = self.keyboard.flush()
            while buffer:
                if buffer[0] == 'c':
                    self.quote.set_text(self.get_quote())
                    self.resize(self.display)
                buffer = buffer[1:]

        self.keyboard.flush()

    def render(self, screen: Display):
        self.text.render(screen)
        self.quote.render(screen)

    def resize(self, display: Display):
        self.text.center(display.size, diff=-Font.height * 1j)
        self.quote.center(display.size, diff=Font.height * 1j)
