import os
from functools import partial
from threading import Thread
from time import sleep
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
from kivymd.uix.textfield import MDTextField

from classes.card import MsCard
from libs.classes_wigdet.asyncimage import AsyncMe
from libs.classes_wigdet.m_cardtextfield import M_CardTextField
from classes.m_loader import M_AKImageLoader, M_AKLabelLoader
from classes.m_cardloader import M_CardLoader
from kivymd_extensions.akivymd.uix.statusbarcolor import change_statusbar_color
from functions import my_queue, return_thread_value

os.environ['SSL_CERT_FILE'] = where()

r = Factory.register
r("M_CardLoader", cls=M_CardLoader)
r("M_AKImageLoader", cls=M_AKImageLoader)
r("M_AKLabelLoader", cls=M_AKLabelLoader)
r("M_CardTextField", cls=M_CardTextField)
r("MsCard", cls=MsCard)
r("AsyncMe", cls=AsyncMe)
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
        change_statusbar_color(self.theme_cls.primary_color)
        Window.bind(on_keyboard=self.on_back_button)
        self.dialog = None
        self.close_dialog = False
        self.login = False
        self.menu = None
        self.label = None
        self.no_screen = ["login", "signup", "initializer", "home"]
        Window.softinput_mode = 'below_target'
        self.theme_cls.font_styles.update({"Money": ["assets/Eczar-Regular", 16, False, 0.5],
                                           "BigMoney": ["assets/Eczar-SemiBold", 20, False, 0.5],
                                           "Small": ["assets/Eczar-SemiBold", 16, False, 0.5]})
        if os.path.exists("theme.txt"):
            with open("theme.txt") as theme:
                self.theme_cls.theme_style = theme.read()

    def build(self):
        for modules in os.listdir("libs/libpy"):
            exec(f"from libs.libpy import {modules.rstrip('.pyc')}")
        return Builder.load_file("manager.kv")

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
        Thread(target=self.initialize_connection).start()

    def initialize_connection(self):
        sleep(1)
        self.root.screens[0].ids.spinner.active = True
        Builder.load_file("libs/kv_widget/widget.kv")
        Builder.load_file("libs/libkv/init/credentials.kv")
        for file in os.listdir("libs/libkv/main"):
            self.root.ids.init.ids.updater.text = f"loading {file.strip('kv')}ns(0.2)"
            sleep(0.1)
            Builder.load_file(f"libs/libkv/main/{file}")
        self.check_add_screen("libs/manager.kv", "Factory.Manager()", "manager")
        self.root.screens[0].ids.spinner.active = False

    def check_add_screen(self, kv_filename, screen_object, screen_name):
        Builder.load_file(kv_filename)
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


NocenStore().run()
