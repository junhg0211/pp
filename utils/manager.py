from display import Display


class Manager:
    def __init__(self):
        self.objects = list()

    def add(self, objet):
        self.objects.append(objet)

    def remove(self, object_):
        if object_ in self.objects:
            self.objects.remove(object_)

    def tick(self):
        removes = set()
        for object_ in self.objects:
            object_.tick()
            if object_.remove:
                removes.add(object_)
        for object_ in removes:
            self.remove(object_)

    def render(self, screen: Display):
        for object_ in self.objects:
            object_.render(screen)

    def resize(self, screen: Display):
        for object_ in self.objects:
            object_.resize(screen)
