from kivy.uix.screenmanager import Screen


class Order(Screen):
    def go_home(self):
        self.manager.current = "home"
