from typing import Optional

from pygame import Surface, draw
from pygame.constants import SRCALPHA


class Font:
    size = 6
    multiplier = 3
    height = size * multiplier
    area = height + multiplier
    characters = 'abcdefghijklmnopqrstuvwxyz.,!?0123456789;:+-*/[]()&|\'" _=#<>%{}\\'

    @staticmethod
    def load(path: str, color: tuple, multiplier: Optional[int] = None) -> 'Font':
        if multiplier is None:
            multiplier = Font.multiplier
        font = Font(multiplier, color)
        with open(path, 'rb') as file:
            buffer = file.read()
        buffer = ''.join(map(lambda x: format(x, '08b'), buffer))
        for i, c in enumerate(Font.characters):
            font.add_surface(c, int(buffer[i * Font.size ** 2: (i + 1) * Font.size ** 2], 2))
        return font

    def __init__(self, multiplier: int, color: tuple):
        self.multiplier = multiplier
        self.color = color
        self.surfaces = dict()

    def add_surface(self, char: str, data: int):
        surface = Surface((Font.size * self.multiplier, Font.size * self.multiplier), SRCALPHA)
        data = format(data, f'0{Font.size ** 2}b')
        for y in range(Font.size):
            for x in range(Font.size):
                if data[y * Font.size + x] == '1':
                    draw.rect(surface, self.color,
                              (x*self.multiplier, y*self.multiplier, self.multiplier, self.multiplier))
        self.surfaces[char] = surface
        return self

    def get_width(self, char: str, kerning: Optional[int] = None) -> int:
        if kerning is None:
            kerning = self.multiplier
        return max((Font.size * self.multiplier + kerning) * len(char) - kerning, 0)

    def render(self, char: str, kerning: Optional[int] = None):
        if kerning is None:
            kerning = self.multiplier
        result = Surface((self.get_width(char, kerning) + kerning, Font.height + kerning), SRCALPHA)
        for i, c in enumerate(char):
            result.blit(self.surfaces[c if c in self.surfaces else '?'], (i * (Font.size * self.multiplier + kerning), 0))
        return result
