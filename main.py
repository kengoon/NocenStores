import os
from functools import partial
from json import dumps, loads, decoder
from os.path import exists
from shutil import rmtree
from threading import Thread
from time import sleep
from certifi import where
from kivy import platform
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.effects.scroll import ScrollEffect
from kivy.loader import Loader
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.properties import StringProperty, ListProperty
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import MagicBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from classes.card import MsCard
from libs.classes_wigdet.asyncimage import AsyncMe
from libs.classes_wigdet.m_cardtextfield import M_CardTextField
from classes.m_loader import M_AKImageLoader, M_AKLabelLoader
from classes.m_cardloader import M_CardLoader
from kivymd_extensions.akivymd.uix.statusbarcolor import change_statusbar_color
from classes.fitimage import M_FitImage
import requests
from jnius import autoclass
from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer

os.environ['SSL_CERT_FILE'] = where()
SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
    packagename=u'org.mindset.nocenstore.nocenstore',
    servicename=u'Notification'
)

r = Factory.register
r("M_CardLoader", cls=M_CardLoader)
r("M_AKImageLoader", cls=M_AKImageLoader)
r("M_AKLabelLoader", cls=M_AKLabelLoader)
r("M_CardTextField", cls=M_CardTextField)
r("MsCard", cls=MsCard)
r("AsyncMe", cls=AsyncMe)
r("M_FitImage", cls=M_FitImage)
Loader.loading_image = "assets/loader.gif"

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
        if exists("assets/compressed"):
            rmtree("assets/compressed")
        change_statusbar_color(self.theme_cls.primary_color)
        Window.bind(on_keyboard=self.on_back_button)
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
        self.no_screen = ["login", "initializer", "home"]
        Window.softinput_mode = 'below_target'
        self.theme_cls.font_styles.update({"Money": ["assets/Eczar-Regular", 16, False, 0.5],
                                           "BigMoney": ["assets/Eczar-SemiBold", 20, False, 0.5],
                                           "Small": ["assets/Eczar-SemiBold", 16, False, 0.5]})
        if os.path.exists("theme.txt"):
            with open("theme.txt") as theme:
                self.theme_cls.theme_style = theme.read()

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
        for modules in os.listdir("libs/libpy"):
            exec(f"from libs.libpy import {modules.rstrip('.pyc')}")
        return Builder.load_file("manager.kv")

    def start_service(self):
        if platform == 'android':
            service = autoclass(SERVICE_NAME)
            mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
            argument = ''
            service.start(mActivity, argument)
            self.service = service

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

    def on_back_button(self, *args):
        if args[1] == 27 and self.root.current == "initializer":
            self.exit_app()
        elif args[1] == 27 and self.root.ids.manager.children[0].current not in self.no_screen:
            self.root.ids.manager.children[0].on_back_button()
        else:
            if args[1] == 27:
                self.exit_app()
        return True

    def on_start(self):
        self.start_service()
        Thread(target=self.initialize_connection).start()

    def initialize_connection(self):
        sleep(1)
        self.root.screens[0].ids.spinner.active = True
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
                print(self.login)
            except decoder.JSONDecodeError:
                os.remove("token.json")
                self.login = False
        Builder.load_file("libs/kv_widget/widget.kv")
        Builder.load_file("libs/libkv/init/credentials.kv")
        Builder.load_file("libs/manager.kv")
        for file in os.listdir("libs/libkv/main"):
            Builder.load_file(f"libs/libkv/main/{file}")
        self.check_add_screen("Factory.Manager()", "manager")
        self.root.screens[0].ids.spinner.active = False

    def check_add_screen(self, screen_object, screen_name):
        Clock.schedule_once(partial(self._add_screen, screen_object, screen_name))

    def _add_screen(self, screen_object, screen_name, _):
        self.root.ids.manager.add_widget(eval(screen_object))
        self.root.current = screen_name

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


class PhoneTextField(MDTextField):
    def insert_text(self, substring, from_undo=False):
        new_text = self.text + substring
        if new_text != '' and len(new_text) < 12:
            MDTextField.insert_text(self, substring, from_undo=from_undo)

    def on_text(self, instance, text):
        instance.error = len(text) != 11


class PhoneCardTextField(M_CardTextField):
    def on_text(self, *args):
        if not args:
            return
        if len(args[1]) > 11:
            self.text = self.text[:-1]


class PlanItem(ThemableBehavior, MagicBehavior, MDBoxLayout):
    text_item = StringProperty()
    border = StringProperty()
    color_select = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_select = self.theme_cls.disabled_hint_text_color
        self.primary = self.theme_cls.primary_color

    def press_on_plan(self, instance_plan):
        self.parent.root.selected_size = self.text_item
        for widget in self.parent.children:
            if widget.color_select == self.primary:
                widget.color_select = self.color_select
                self.grow()
                break
        instance_plan.color_select = self.primary


NocenStore().run()
