import os
from functools import partial
from threading import Thread
from time import sleep

from kivy import platform
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.effects.scroll import ScrollEffect
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.lang import Builder

from classes.card import MsCard
from libs.classes_wigdet.m_cardtextfield import M_CardTextField
from kivy.factory import Factory
from classes.m_loader import M_AKImageLoader, M_AKLabelLoader
from classes.m_cardloader import M_CardLoader

r = Factory.register
r("M_CardLoader", cls=M_CardLoader)
r("M_AKImageLoader", cls=M_AKImageLoader)
r("M_AKLabelLoader", cls=M_AKLabelLoader)
r("M_CardTextField", cls=M_CardTextField)
r("MsCard", cls=MsCard)
exec("import akivymd")

if platform == "android":
    from android.permissions import Permission, request_permissions

    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])


class NocenStore(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu = None
        self.label = None
        self.theme_cls.primary_palette = "Green"
        Window.softinput_mode = 'below_target'
        self.theme_cls.font_styles.update({"Money": ["assets/Eczar-Regular", 16, False, 0.5]})
        if os.path.exists("theme.txt"):
            with open("theme.txt") as theme:
                self.theme_cls.theme_style = theme.read()

    def build(self):
        for modules in os.listdir("libs/libpy"):
            exec(f"from libs.libpy import {modules.rstrip('.pyc')}")
        # Builder.load_file("libs/libkv/init/credentials.kv")
        return Builder.load_file("manager.kv")

    def on_start(self):
        Thread(target=self.initialize_connection).start()

    def initialize_connection(self):
        sleep(1)
        self.root.screens[0].ids.spinner.active = True
        Builder.load_file("libs/kv_widget/widget.kv")
        # Builder.load_file("libs/manager.kv")
        Builder.load_file("libs/libkv/init/credentials.kv")
        for file in os.listdir("libs/libkv/main"):
            Builder.load_file(f"libs/libkv/main/{file}")
        sleep(4)
        self.check_add_screen(
            "libs/manager.kv", "Factory.Manager()", "manager")
        # self.check_add_screen(
        #     "libs/libkv/init/credentials.kv", ["Factory.Login()", "Factory.SignUp()"],
        #     "login", "from libs.libpy import credentials")
        self.root.screens[0].ids.spinner.active = False

    def check_add_screen(self, kv_filename, screen_object: list, screen_name):
        # if self.root.has_screen(screen_name):
        #     self.root.current = screen_name
        #     return
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


NocenStore().run()