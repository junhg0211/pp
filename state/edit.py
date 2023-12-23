from math import log10, ceil
from os.path import isfile, join

from pygame import draw
from pygame.constants import K_LEFT, K_RIGHT, K_UP, K_DOWN, K_LSHIFT, K_LCTRL, K_r

from display import Display
from objects import Text
from objects.toast import Toast
from state import State
from utils import color, global_manager, Font
from utils.functions import center, limit


class Edit(State):
    background = color.DARK_GREY

    def __init__(self, filename: str = ''):
        global_manager.get_global('action_guide').set_actions({
            '': '&#)',
            K_LSHIFT: {
                '': '&',
                's': 'save',
                'o': 'open',
                'r': 'rename',
                'd': 'rm ln',
                'x': 'exit'
            },
            K_LCTRL: {
                '': '#',
                'r': 'run'
            }
        })
        self.keyboard = global_manager.get_global('keyboard')
        self.keyboard.flush()

        if filename:
            self.filename = filename
        else:
            self.filename = 'untitled.ppp'
        self.content_front = ''
        self.content_back = ''

        self.display = global_manager.get_global('display')

        self.font = Font.load('res/font/ppaa.ppf', color.WHITE)
        self.filename_text = Text(0, self.filename, self.font)

        self.camera_line = 0
        self.cursor_pos = [0, 0]
        self.content_y = Font.height + Font.multiplier * 3
        self.max_lines = int((self.display.size.imag - self.content_y * 2) // Font.area)

        self.resize(self.display)
        self.open(self.filename)

    def pop_line(self, line_number: int) -> str:
        lines = (self.content_front + self.content_back).split('\n')
        result = lines.pop(line_number).strip()
        self.content_front = '\n'.join(lines[:line_number])
        self.content_back = '\n' + '\n'.join(lines[line_number:])
        return result

    def open(self, filename: str):
        path = join('out', filename)
        objet_manager = global_manager.get_global('objet_manager')
        if isfile(path):
            self.content_front, self.content_back = '', ''
            with open(path, 'r') as file:
                self.content_back = file.read()
            self.filename = filename
            objet_manager.add(Toast('loaded ' + filename))
        else:
            objet_manager.add(Toast('file not found'))

    def tick(self):
        buffer = ""
        if self.keyboard.is_pressed(K_LSHIFT):
            buffer = self.keyboard.flush()
            while buffer:
                if buffer[0] == 'x':
                    global_manager.set_global('state', ('initial',))
                elif buffer[0] == 'r':
                    self.filename = self.pop_line(self.cursor_pos[0])
                    self.keyboard.flush()
                elif buffer[0] == 's':
                    open('out/' + self.filename, 'w').write(self.content_front + self.content_back)
                    self.keyboard.flush()
                    global_manager.get_global('objet_manager').add(Toast(f'{len(self.content_front + self.content_back)} '
                                                                         f'characters\nsaved on {self.filename}'))
                elif buffer[0] == 'o':
                    self.open(self.pop_line(self.cursor_pos[0]))
                    self.keyboard.flush()
                elif buffer[0] == 'd':
                    self.pop_line(self.cursor_pos[0])
                    self.keyboard.flush()
                else:
                    break
                buffer = buffer[1:]
        elif self.keyboard.is_pressed(K_LCTRL):
            if self.keyboard.is_down(K_r):
                global_manager.set_global('state', ('run', self.filename))

        buffer += self.keyboard.flush()
        while buffer:
            if buffer[0] == '\b':
                self.content_front, buffer = self.content_front[:-1], buffer[1:]
            elif buffer[0] == '\r':
                self.content_front, buffer = self.content_front + '\n', buffer[1:]
            elif buffer[0] == '\000':
                length = buffer[1:].index('\000')
                key_code = int(buffer[1:length+1])
                if key_code == K_LEFT:
                    if self.content_front:
                        self.content_front, character = self.content_front[:-1], self.content_front[-1]
                        self.content_back = character + self.content_back
                elif key_code == K_RIGHT:
                    if self.content_back:
                        character, self.content_back = self.content_back[0], self.content_back[1:]
                        self.content_front += character
                elif key_code == K_UP:
                    if '\n' in self.content_front:
                        front_lines = self.content_front.split('\n')
                        # noinspection PyUnresolvedReferences
                        self.content_back = front_lines[-2][self.cursor_pos[1]:] + '\n' + front_lines[-1] \
                            + self.content_back
                        del front_lines[-1]
                        front_lines[-1] = front_lines[-1][:self.cursor_pos[1]]
                        self.content_front = '\n'.join(front_lines)
                    else:
                        self.content_front, self.content_back = '', self.content_front + self.content_back
                elif key_code == K_DOWN:
                    if '\n' in self.content_back:
                        back_lines = self.content_back.split('\n')
                        self.content_front += back_lines[0] + '\n' + back_lines[1][:self.cursor_pos[1]]
                        del back_lines[0]
                        back_lines[0] = back_lines[0][self.cursor_pos[1]:]
                        self.content_back = '\n'.join(back_lines)
                    else:
                        self.content_front, self.content_back = self.content_front + self.content_back, ''
                        self.camera_line += 1
                buffer = buffer[length + 2:]
            else:
                break
        self.content_front += buffer
        self.cursor_pos = [self.content_front.count('\n'), len(self.content_front[::-1].split('\n', 1)[0])]
        self.camera_line = limit(self.camera_line, self.cursor_pos[0] - self.max_lines + 1, self.cursor_pos[0])

        self.filename_text.set_text(f'{self.filename} - {self.cursor_pos[0] + 1}:{self.cursor_pos[1]}')
        self.resize(self.display)

    def render(self, screen: Display):
        self.filename_text.render(screen)
        content = self.content_front + self.content_back
        number_strip_column = ceil(log10(content.count('\n') + 2)) + 1

        draw.rect(screen.window, color.GREY, (
            ((self.cursor_pos[1] + number_strip_column) * Font.area + Font.multiplier,
             self.content_y + Font.area * (self.cursor_pos[0] - self.camera_line)), (Font.height, Font.height)))

        for i, line in enumerate(content.split('\n')[self.camera_line:self.camera_line + self.max_lines]):
            i += self.camera_line
            content_text = Text(complex(Font.multiplier, self.content_y + Font.area * (i - self.camera_line)),
                                f'{format(i+1, f"{number_strip_column-1}d")} {line}', self.font)
            content_text.render(screen)

    def resize(self, screen: Display):
        self.filename_text.pos = complex(center(screen.size.real, self.font.get_width(self.filename_text.text)),
                                         Font.multiplier)
