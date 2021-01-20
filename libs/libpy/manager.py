from kivy.uix.screenmanager import ScreenManager


class Manager(ScreenManager):
    prev_screen = []
    
    def on_next_screen(self, prev_screen):
        self.prev_screen.append(prev_screen)

    def on_back_button(self):
        self.current = self.prev_screen.pop()
    pass
