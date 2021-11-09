import os
from functools import partial
from json import dumps, loads, decoder
from os.path import exists
from shutil import rmtree
from threading import Thread
from time import sleep

from kivy.config import Config

Config.set("kivy", "log_level", "debug")

from certifi import where
from kivy import platform
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.effects.scroll import ScrollEffect
from kivy.loader import Loader
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.factory import Factory
from kivymd.app import MDApp
from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer

os.environ['SSL_CERT_FILE'] = where()
SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
    packagename=u'org.mindset.nocenstore.nocenstore',
    servicename=u'Notification'
)

Loader.loading_image = "assets/loader.gif"
font_folder = "assets/font/"

if platform == "android":
    from android.permissions import Permission, request_permissions

    request_permissions(
        [Permission.READ_EXTERNAL_STORAGE,
         Permission.WRITE_EXTERNAL_STORAGE,
         Permission.CALL_PHONE,
         Permission.CALL_PRIVILEGED]
    )


class NocenStore(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "A700"
        if exists("assets/compressed"):
            rmtree("assets/compressed")
        Window.bind(on_key_up=self.on_back_button)
        Window.bind(on_keyboard=self.on_ignore)
        # Window.bind(on_flip=self.fix_back_button)
        self.login_widget = False
        self.signup_widget = False
        self.lookout_widget = False
        self.electronics_widget = False
        self.portables_widget = False
        self.furniture_widget = False
        self.clothing_widget = False
        self.beauty_widget = False
        self.kitchen_widget = False
        self.setting_widget = False
        self.customer_care_widget = False
        self.deals_widget = False
        self.order_widget = False
        self.student_info_widget = False
        self.search_widget = False
        self.saved_product_widget = False
        self.cart_widget = False
        self.checkout_widget = False
        self.payment_widget = False
        self.data_product = []
        self.current_email = ""
        self.current_phone = ""
        self.total_payment = ""
        self.current_location = ""
        self.dialog = None
        self.service = None
        self.on_service = None
        self.server = None
        self.theme_no_active = False
        self.firebase = {}
        self.current = ""
        self.login = None
        self.client = None
        self.url = "https://nocenstore.pythonanywhere.com/"
        self.close_dialog = False
        self.menu = None
        if exists("token.json"):
            with open("token.json", "r") as file:
                self.firebase = loads(file.read())
        self.token = None
        self.label = None
        self.no_screen = ["initializer", "home"]
        Window.softinput_mode = 'below_target'
        self.theme_cls.font_styles.update(
            {
                "H1": [f"{font_folder}DINAlternate-bold", 96, False, -1.5],
                "H2": [f"{font_folder}avenir_heavy", 60, False, -0.5],
                "H3": [f"{font_folder}DINAlternate-bold", 48, False, 0],
                "H4": [f"{font_folder}avenir_heavy", 34, False, 0.25],
                "H5": [f"{font_folder}DINAlternate-bold", 24, False, 0],
                "H6": [f"{font_folder}avenir_heavy", 20, False, 0.15],
                "Button": [f"{font_folder}DINAlternate-bold", 14, True, 1.25],
                "Body1": [f"{font_folder}avenir_heavy", 16, False, 0.5],
                "Body2": [f"{font_folder}avenir_heavy", 14, False, 0.25],
                "Money": ["assets/font/DINAlternate-bold", 16, False, 0.5],
                "BigMoney": ["assets/font/avenir_heavy", 20, False, 0.5],
                "Small": ["assets/font/DINAlternate-bold", 16, False, 0.5],
                "Naira": ["assets/font/iconfont", 16, False, 0.5]
            }
        )
        if os.path.exists("theme.txt"):
            with open("theme.txt") as theme:
                self.theme_cls.theme_style = theme.read()

    @staticmethod
    def fix_back_button(*args):
        if platform == "android":
            from kvdroid import activity
            from android.runnable import run_on_ui_thread

            @run_on_ui_thread
            def fix():
                activity.onWindowFocusChanged(False)
                activity.onWindowFocusChanged(True)

            fix()

    def build(self):
        self.server = server = OSCThreadServer()
        server.listen(
            address='localhost',
            port=3001,
            default=True,
        )
        server.bind(b'/message', self.display_message)
        server.bind(b'/date', self.date)

        self.client = OSCClient('localhost', 3000)
        return Builder.load_file("manager.kv")

    def start_service(self):
        if platform == 'android':
            pass
            # service = autoclass(SERVICE_NAME)
            # mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
            # argument = ''
            # service.start(mActivity, argument)
            # self.service = service

        # elif platform in ('linux', 'linux2', 'macos', 'win'):
        #     from runpy import run_path
        #     from threading import Thread
        #     self.service = Thread(
        #         target=run_path,
        #         args=['service.py'],
        #         kwargs={'run_name': '__main__'},
        #         daemon=True
        #     )
        #     self.service.start()
        # else:
        #     raise NotImplementedError(
        #         "service start not implemented on this platform"
        #     )

    def display_message(self, message):
        print(message)

    def date(self, message):
        print(message)

    def on_ignore(self, *args):
        if args[1] == 27:
            return True

    def on_back_button(self, *args):
        if args[1] == 27 and self.root.current == "initializer":
            self.exit_app()
        elif args[1] == 27 and self.root.ids.manager.children[0].current not in self.no_screen:
            self.root.ids.manager.children[0].on_back_button()
            if self.current == "profile":
                self.root.ids.manager.children[0].ids.home.ids.home.dispatch("on_release")
            if self.current == "lookout":
                self.root.ids.manager.children[0].ids.lookout.update_interface(
                    self.root.ids.manager.children[0].ids.lookout.tmp_data)
        else:
            if args[1] == 27:
                self.exit_app()
        return True

    def on_start(self):
        print("stopped")
        if exists("tmp"):
            import shutil
            shutil.rmtree("tmp")
        self.start_service()
        Thread(target=self.initialize_connection).start()

    def initialize_connection(self):
        from libs.classes_wigdet.m_cardtextfield import M_CardTextField
        from classes.m_loader import M_AKImageLoader, M_AKLabelLoader
        from classes.m_cardloader import M_CardLoader
        from classes.fitimage import FitImage as M_FitImage
        r = Factory.register
        r("M_CardLoader", cls=M_CardLoader)
        r("M_AKImageLoader", cls=M_AKImageLoader)
        r("M_AKLabelLoader", cls=M_AKLabelLoader)
        r("M_CardTextField", cls=M_CardTextField)
        r("M_FitImage", cls=M_FitImage)
        import requests
        if self.firebase:
            try:
                data = requests.post(url=self.url,
                                     data=dumps({"refreshToken": self.firebase["refreshToken"], "version": "0.2"}))
                if data.text:
                    with open("token.json", "w") as file:
                        new_data = loads(data.text)
                        file.write(dumps(new_data, indent=4))
                    self.login = True
            except requests.exceptions.RequestException:
                self.login = True
            except decoder.JSONDecodeError:
                os.remove("token.json")
                self.login = False
        Builder.load_file("imports.kv")
        Builder.load_file("libs/kv_widget/widget.kv")
        for modules in os.listdir("libs/libpy"):
            if "initializer" in modules:
                continue
            exec(f"from libs.libpy import {modules.rstrip('.pyc')}")
        Builder.load_file("libs/libkv/init/credentials.kv")
        Builder.load_file("libs/manager.kv")
        for file in os.listdir("libs/libkv/main"):
            Builder.load_file(f"libs/libkv/main/{file}")
        self.check_add_screen("Factory.Manager()", "manager")

    def check_add_screen(self, screen_object, screen_name):
        Clock.schedule_once(partial(self._add_screen, screen_object, screen_name))

    def _add_screen(self, screen_object, screen_name, _):
        self.root.ids.manager.add_widget(eval(screen_object))
        Clock.schedule_once(lambda x: exec(
            "self.root.current = screen_name", {"self": self, "screen_name": screen_name}), 4)

    @staticmethod
    def open(menu, label):
        if not menu.ids.md_menu.children[0].children:
            label.size_hint_y = None
            label.height = dp(100)
            menu.ids.md_menu.effect_cls = ScrollEffect
            menu.ids.md_menu.children[0].padding = [dp(10), dp(5), dp(5), dp(10)]
            menu.ids.md_menu.children[0].add_widget(label)
        menu.open()

    def exit_app(self):
        from kivymd.uix.button import MDRaisedButton, MDFlatButton
        if platform == "android":
            from kvdroid import activity
            activity.moveTaskToBack(True)
            return
        if self.close_dialog:
            self.dialog.dismiss()
            self.close_dialog = False
            return

        def exit_app(*args):
            self.stop()

        def dismiss_dialog(*args):
            self.dialog.dismiss()
            self.close_dialog = False

        button1 = MDFlatButton(text="Cancel", on_release=dismiss_dialog)
        button2 = MDRaisedButton(text="Continue", on_release=exit_app)
        from kivymd.uix.dialog import MDDialog
        self.dialog = MDDialog(
            title="Exit App",
            text="Do you want to exit NocenStore",
            buttons=[button1, button2], auto_dismiss=False,
            size_hint_x=None,
            width=Window.width - dp(20)
        )
        self.dialog.open()
        self.close_dialog = True

    @staticmethod
    def on_focus(value):
        if platform == "android":
            from kvdroid import activity
            from android.runnable import run_on_ui_thread

            @run_on_ui_thread
            def fix_back_button():
                activity.onWindowFocusChanged(False)
                activity.onWindowFocusChanged(True)

            if not value:
                fix_back_button()

    def on_stop(self):
        if exists("tmp"):
            import shutil
            shutil.rmtree("tmp")


NocenStore().run()
