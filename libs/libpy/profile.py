import os

from jnius import autoclass
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.utils import get_color_from_hex, platform
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
        self.alert = SweetAlert(size_hint_x=None, width=Window.width - dp(20))
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
            notify("please login to continue")
            self.app.current = self.name
            self.root.manager.prev_screen.append(self.root.name)
            self.root.manager.current = "login"

    def to_next(self, screen):
        self.root.manager.on_next_screen(self.root.name)
        self.root.manager.current = screen

    def logout(self):
        self.alert.fire("You Are About To Logout", type="info", buttons=[self.CONTINUE, self.CANCEL])

    def delete_token(self):
        self.alert.dismiss()
        try:
            os.remove("token.json")
        except FileNotFoundError:
            pass
        self.app.firebase = {}
        self.app.current = self.name
        self.root.manager.prev_screen.append(self.root.name)
        self.root.manager.current = "login"

    @staticmethod
    def share_app():
        if platform == "android":
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            Intent = autoclass('android.content.Intent')
            String = autoclass("java.lang.String")
            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.putExtra(Intent.EXTRA_TEXT, String(
                "Buy and Sell Your Goods Faster at NocenStore "
                "https://play.google.com/store/apps/details?id=org.mindset.nocenstore.nocenstore"
            ))
            intent.setType("text/plain")
            chooser = Intent.createChooser(intent, String('Share'))
            mActivity.startActivity(chooser)
