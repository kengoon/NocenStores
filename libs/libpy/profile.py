import os
import webbrowser
from kivy.clock import mainthread, Clock
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen
from kivy.utils import get_color_from_hex, platform
from kivy.app import App
from kivymd.uix.button import MDRaisedButton

from classes.notification import notify
from kivymd_extensions.sweetalert import SweetAlert


class Profile(Screen):
    app = App.get_running_app()
    update = False
    menu = None
    alert = ObjectProperty()
    root = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        self.screens = {
            "customer care": ["Factory.CustomerCare()", "customer_care_widget"],
            "setting": ["Factory.Setting()", "setting_widget"],
            "order": ["Factory.Order()", "order_widget"],
            "saved items": ["Factory.SavedProduct()", "saved_product_widget"],
        }
        self.dialog = ModalView(size_hint=(.5, .5), background="", background_color=[0, 0, 0, 0])
        self.dialog.add_widget(Factory.RequestDialog(
            text="checking for tickets.....",
            dialog=self.dialog,
            btn_disabled=True,
            icon="ticket"
        ))
        self.dialog.auto_dismiss = False
        self.webview = None

    def on_enter(self, *args):
        if not self.alert:
            self.alert = SweetAlert()
        if not self.app.login:
            notify("please login to continue")
            self.app.current = self.name
            self.root.manager.prev_screen.append(self.root.name)
            from tools import check_add_widget
            check_add_widget(self.app, "login_widget", self.root, "Factory.Login()", "login")
            self.root.manager.current = "login"

    def to_next(self, screen):
        self.root.manager.on_next_screen(self.root.name)
        from tools import check_add_widget
        check_add_widget(
            self.app, self.screens[screen][1], self.root, self.screens[screen][0], screen.split(" ")[0])
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
        self.app.login = False
        self.app.current = self.name
        self.root.manager.prev_screen.append(self.root.name)
        from tools import check_add_widget
        check_add_widget(self.app, "login_widget", self.root, "Factory.Login()", "login")
        self.root.manager.current = "login"

    @staticmethod
    def share_app():
        if platform == "android":
            from jnius import autoclass
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

    def get_ticket(self):
        self.request_dialog()
        import requests
        while True:
            try:
                url = requests.get("https://nocenstore.pythonanywhere.com/ticket")
                if not url.text:
                    return notify("NO TICKETS FOR NOW", duration=7)
                self.open_url(url.text) if platform == "android" else webbrowser.open(url.text)
                break
            except requests.exceptions.RequestException:
                Clock.schedule_once(lambda dt: self.dialog.dismiss())
                return notify("NETWORK ERROR, PLEASE TRY AGAIN....")

    @mainthread
    def open_url(self, url):
        self.dialog.dismiss()
        from jnius import JavaException
        from kvdroid.jimplement.customtabs import launch_url
        try:
            launch_url(url)
        except JavaException:
            from android_webview import WebView
            if not self.webview:
                self.webview = WebView(
                    enable_javascript=True,
                    enable_downloads=False,
                    enable_zoom=False,
                )
            self.app.current = "webview"
            self.webview.url = url
            self.webview.open()

    @mainthread
    def request_dialog(self):
        self.dialog.open()

