from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu


class Profile(Screen):
    update = False
    menu = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_setting(self):
        self.root.manager.on_next_screen(self.root.name)
        self.root.manager.current = "setting"
