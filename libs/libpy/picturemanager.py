from kivy.uix.screenmanager import Screen


class PictureManager(Screen):
    def _go_back(self, screen):
        self.manager.current = "home"
    pass