from os import listdir
from os.path import join

from pygame import K_LSHIFT, K_x, K_e, K_r

from display import Display
from objects import Text
from state import State
from utils import global_manager, color, Font
from utils.functions import center, limit


class Files(State):
    background = color.WHITE

    def __init__(self):
        global_manager.get_global('action_guide').set_actions({
            '': '&)',
            'j': 'next file',
            'k': 'previous file',
            K_LSHIFT: {
                '': '&',
                'x': 'back',
                'e': 'edit',
                'r': 'run'
            }
        })
        display = global_manager.get_global('display')
        self.keyboard = global_manager.get_global('keyboard')

        font = Font.load('res/font/ppaa.ppf', color.BLACK)

        self.directory = './'
        self.files = [f for f in sorted(listdir(join('out', self.directory)))]
        self.files_surface = [font.render(f) for f in self.files]
        self.selected_star = font.render('*')
        self.display_line_count = (display.size.imag - Font.area * 2) // Font.area

        self.selected_index = 0
        self.scroll = 0

        self.title_text = Text(0, self.directory, font)

        self.resize(display)

    def tick(self):
        if self.keyboard.is_pressed(K_LSHIFT):
            if self.keyboard.is_down(K_x):
                global_manager.set_global('state', ('initial',))
            elif self.keyboard.is_down(K_e):
                global_manager.set_global('state', ('edit', join(self.directory, self.files[self.selected_index])))
            elif self.keyboard.is_down(K_r):
                global_manager.set_global('state', ('run', join(self.directory, self.files[self.selected_index])))
        else:
            buffer = self.keyboard.flush()
            while buffer:
                if buffer[0] == 'j':
                    self.selected_index += 1
                    buffer = buffer[1:]
                elif buffer[0] == 'k':
                    self.selected_index -= 1
                    buffer = buffer[1:]
                else:
                    break

        self.selected_index = limit(self.selected_index, 0, len(self.files) - 1)

    def render(self, screen: Display):
        self.title_text.render(screen)

        for i in range(self.scroll, min(self.scroll + self.display_line_count, len(self.files))):
            screen.window.blit(self.files_surface[i], (Font.area, i * Font.area + Font.area))
            if self.selected_index == i:
                screen.window.blit(self.selected_star, (0, i * Font.area + Font.area))

    def resize(self, screen: Display):
        self.title_text.pos = complex(center(screen.size.real, self.title_text.font.get_width(self.title_text.text)),
                                      Font.multiplier)
