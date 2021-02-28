from kivy.uix.screenmanager import Screen


class Deals(Screen):
    def go_home(self):
        self.manager.current = "home"
