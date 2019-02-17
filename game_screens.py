class Screen:

    def __init__(self, screen):
        self.widget_list = []
        self.wigets_to_return = []
        self.screen = screen

    def add(self, widget, to_return=False):
        self.widget_list.append(widget)
        if to_return:
            self.wigets_to_return.append(widget)
