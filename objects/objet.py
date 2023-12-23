from display import Display
from utils import global_manager


class Objet:
    def __init__(self, pos: complex):
        self.pos = pos
        self.remove = False

    def center(self, screen_size: complex = 0+0j, size: complex = 0+0j, diff: complex = 0+0j) -> 'Objet':
        if not size:
            size = self.get_size()
        if not screen_size:
            screen_size = global_manager.get_global('display').size
        self.pos = (screen_size - size) / 2 + diff
        return self

    def get_size(self) -> complex:
        raise NotImplementedError

    def resize(self, screen: Display):
        raise NotImplementedError

    def tick(self):
        pass

    def render(self, screen: Display):
        pass
