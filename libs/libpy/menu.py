from kivy.uix.screenmanager import Screen


class Menu(Screen):
    def go_home(self):
        self.manager.current = "home"
    pass
