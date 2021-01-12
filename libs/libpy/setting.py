from kivy.uix.screenmanager import Screen


class Setting(Screen):
    def go_home(self):
        self.manager.current = "home"
    pass
