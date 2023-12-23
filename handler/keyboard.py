from time import time

from pygame.constants import KEYDOWN, KEYUP
from pygame.event import Event

from handler import Handler


class Keyboard(Handler):
    hold = 0.5
    repeat = 1/20

    def __init__(self):
        self.keys = set()

        self.previous_keys = set()
        self.down_keys = set()
        self.up_keys = set()

        self.last_unicode_pressed = ''
        self.last_key_pressed = -1
        self.cool = 0
        self.last_update = time()
        self.last_key_pressed_time = time()
        self.buffer = ''
        self.recording = False

    def buffer_add(self):
        if not self.last_unicode_pressed:
            self.buffer += f'\000{self.last_key_pressed}\000'
        else:
            self.buffer += self.last_unicode_pressed

    def handle(self, event: Event):
        if event.type == KEYDOWN:
            self.keys.add(event.key)
            self.last_unicode_pressed = event.unicode.lower()
            self.last_key_pressed = event.key
            self.last_key_pressed_time = time()
            self.cool = Keyboard.hold
            self.buffer_add()
        elif event.type == KEYUP:
            if event.key in self.keys:
                self.keys.remove(event.key)

    def flush(self) -> str:
        buffer = self.buffer
        self.buffer = ''
        return buffer

    def prepare(self):
        self.down_keys = self.keys - self.previous_keys
        self.up_keys = self.previous_keys - self.keys

        now = time()
        if self.last_key_pressed in self.keys:
            delta_time = now - self.last_update
            self.cool -= delta_time
            if self.cool <= 0:
                self.buffer_add()
                self.cool += 1 / (now - self.last_key_pressed_time + 1) * Keyboard.repeat

        self.last_update = now

    def tidy(self):
        self.previous_keys = self.keys.copy()

    def is_pressed(self, key: int) -> bool:
        return key in self.keys

    def is_down(self, key: int) -> bool:
        return key in self.down_keys

    def is_up(self, key: int) -> bool:
        return key in self.up_keys

