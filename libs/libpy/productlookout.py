from kivy.uix.screenmanager import Screen


class ProductLookOut(Screen):
    def go_home(self):
        self.manager.current = "home"
    pass
