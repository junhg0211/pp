from display import Display
from utils import color


class State:
    background = color.GREY

    def tick(self):
        pass

    def tidy(self):
        pass

    def render(self, screen: Display):
        pass

    def resize(self, screen: Display):
        raise NotImplementedError
