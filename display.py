from typing import Callable

from pygame import display, image
from pygame.constants import RESIZABLE, VIDEORESIZE
from pygame.event import Event
from pygame.time import Clock


class Display:
    @staticmethod
    def update():
        display.flip()

    def __init__(self, width: int, height: int, caption: str, icon_path: str, resize_function: Callable,
                 desired_fps: int = 60):
        self.size = complex(width, height)
        self.resize_function = resize_function
        self._desired_fps = desired_fps

        display.set_caption(caption)
        display.set_icon(image.load(icon_path))
        self.window = display.set_mode((self.size.real, self.size.imag), RESIZABLE)

        self._clock = Clock()

    def handle(self, event: Event):
        if event.type == VIDEORESIZE:
            self.size = complex(*event.size)
            self.window = display.set_mode((self.size.real, self.size.imag), RESIZABLE)
            self.resize_function()

    def out(self):
        self._clock.tick(self._desired_fps)
