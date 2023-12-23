from os.path import join

from pygame.constants import K_LSHIFT, K_x, K_e

from display import Display
from state import State
from utils import color, Interpreter, global_manager, Font


class Run(State):
    background = color.DARK_GREY

    def __init__(self, path: str):
        global_manager.get_global('action_guide').set_actions({
            '': '&)',
            'j': 'scroll down',
            'k': 'scroll up',
            K_LSHIFT: {
                '': '&',
                'x': 'quit',
                'e': 'edit'
            }
        })
        self.keyboard = global_manager.get_global('keyboard')
        self.scroll = 0
        self.display_line_count = int((global_manager.get_global('display').size.imag - Font.area) / Font.area)

        self.path = path
        self.interpreter = Interpreter(join('out', self.path))
        self.end = False

        self.font = Font.load('res/font/ppaa.ppf', color.WHITE)
        self.outs = list()

    def tick(self):
        if self.keyboard.is_pressed(K_LSHIFT):
            if self.keyboard.is_down(K_x):
                global_manager.set_global('state', ('initial',))
            elif self.keyboard.is_down(K_e):
                global_manager.set_global('state', ('edit', self.path))
        else:
            buffer = self.keyboard.flush()
            while buffer:
                if buffer[0] == 'j':
                    self.scroll += 1
                elif buffer[0] == 'k':
                    self.scroll -= 1
                buffer = buffer[1:]

        if not self.end:
            if flush := self.interpreter.flush():
                for line in flush:
                    self.outs.append(self.font.render(str(line)))
            result = self.interpreter.tick()
            if result:
                self.end = True
                try:
                    self.interpreter.close()
                except EOFError:
                    pass

    def render(self, screen: Display):
        start = max(0, self.scroll)
        for i in range(start, min(len(self.outs), start + self.display_line_count)):
            out = self.outs[i]
            screen.window.blit(out, (0, Font.area * (i - self.scroll)))

    def resize(self, screen: Display):
        pass
