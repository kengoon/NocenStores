from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from classes.notification import notify


class Profile(Screen):
    app = MDApp.get_running_app()
    update = False
    menu = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self, *args):
        if not self.app.login:
            print(self.app.login)
            notify("please login to continue")
            self.app.current = self.name
            self.root.manager.current = "login"

    def to_next(self, screen):
        self.root.manager.on_next_screen(self.root.name)
        self.root.manager.current = screen
