import os

from kivy.uix.screenmanager import Screen
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton

from classes.notification import notify
from kivymd_extensions.sweetalert import SweetAlert


class Profile(Screen):
    app = MDApp.get_running_app()
    update = False
    menu = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alert = SweetAlert()
        self.CONTINUE = MDRaisedButton(
            text='CONTINUE',
            font_size=16,
            on_release=lambda x: self.delete_token(),
        )
        self.CANCEL = MDRaisedButton(
            text='CANCEL',
            font_size=16,
            on_release=lambda x: self.alert.dismiss()
        )
        self.CANCEL.md_bg_color = get_color_from_hex('#dd3b34')

    def on_enter(self, *args):
        if not self.app.login:
            print(self.app.login)
            notify("please login to continue")
            self.app.current = self.name
            self.root.manager.current = "login"

    def to_next(self, screen):
        self.root.manager.on_next_screen(self.root.name)
        self.root.manager.current = screen

    def logout(self):
        self.alert.fire("You Are About To Logout", type="info", buttons=[self.CONTINUE, self.CANCEL])

    def delete_token(self):
        self.alert.dismiss()
        os.remove("token.json")
        self.root.manager.current = "login"
