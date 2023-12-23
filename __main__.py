from pygame.constants import QUIT
from pygame.event import get as get_events, Event

from display import Display
from handler import Keyboard
from objects import ActionGuide
from state import Initial, State, Edit, Files, Run
from utils import Manager, global_manager, Font


class Program:
    def __init__(self, width: int, height: int, caption: str, icon_path: str):
        self.display = global_manager.set_global('display', Display(width, height, caption, icon_path, self.resize))

        self.keyboard = global_manager.set_global('keyboard', Keyboard())
        self.objet_manager = global_manager.set_global('objet_manager', Manager())
        self.objet_manager.add(global_manager.set_global('action_guide', ActionGuide()))
        global_manager.set_global('state', Initial())

        self._running = True

    def resize(self):
        self.objet_manager.resize(self.display)
        global_manager.get_global('state').resize(self.display)

    def handle(self, event: Event):
        """ 이벤트를 받고 처리합니다. """
        if event.type == QUIT:
            self._running = False
        self.keyboard.handle(event)
        self.display.handle(event)

    def prepare(self):
        """ 이번 tick에서 사용할 변수들을 준비합니다. """
        self.keyboard.prepare()

    def tick(self):
        """ 요소들을 한 프레임 진행합니다. """
        self.objet_manager.tick()
        global_manager.get_global('state').tick()

    def tidy(self):
        """ 다음 tick에서 사용할 자료를 정리합니다. tick 이후에 실행됩니다. """
        self.keyboard.tidy()
        state = global_manager.get_global('state')
        if not isinstance(state, State):
            if state[0] == 'initial':
                global_manager.set_global('state', Initial())
            elif state[0] == 'new':
                global_manager.set_global('state', Edit())
            elif state[0] == 'edit':
                global_manager.set_global('state', Edit(state[1]))
            elif state[0] == 'files':
                global_manager.set_global('state', Files())
            elif state[0] == 'run':
                global_manager.set_global('state', Run(state[1]))
            elif state[0] == 'exit':
                self._running = False

    def render(self):
        """ 화면에 그립니다. """
        state = global_manager.get_global('state')
        if not isinstance(state, State):
            return

        self.display.window.fill(state.background)

        state.render(self.display)
        self.objet_manager.render(self.display)

        self.display.update()

    def out(self):
        """ render가 끝나고 한 번 실행합니다. """
        self.display.out()

    def run(self):
        while self._running:
            for event in get_events():
                self.handle(event)

            self.prepare()
            self.tick()
            self.tidy()

            self.render()
            self.out()


if __name__ == '__main__':
    program = Program(Font.height * 60, Font.height * 50, 'pp', 'res/image/icon.png')
    program.run()
