from threading import Thread

from kivy.event import EventDispatcher
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock, mainthread
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivymd.uix.menu import MDDropdownMenu


class Home(Screen, EventDispatcher):
    app = MDApp.get_running_app()
    clock = ObjectProperty()
    counter = NumericProperty(0)
    update = False
    menu = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_menu")

    def on_enter(self, *args):
        self.clock = Clock.schedule_interval(self._start_animation, 5)
        if not self.update:
            self.ids.home.header.ids._label.font_style = "Caption"
            self.ids.new.header.ids._label.font_style = "Caption"
            self.ids.sell.header.children[0].remove_widget(self.ids.sell.header.ids._label)
            self.ids.sell.header.ids._label_icon.pos_hint = {"center_x": .5, "center_y": .5}
            self.ids.sell.header.ids._label_icon.font_size = dp(35)
            self.ids.used.header.ids._label.font_style = "Caption"
            self.ids.info.header.ids._label.font_style = "Caption"
            self.menu = MDDropdownMenu(
                caller=self.ids.menu,
                items=[
                    {"icon": "account", "text": "profile"},
                    {"icon": "cog", "text": "settings"},
                ],
                width_mult=4,
                position="auto"
            )
            self.update = True

    def on_leave(self, *args):
        self._stop_animation()

    def _start_animation(self, *args):
        self.counter += 1
        if self.counter == 3:
            self.counter = 0
        self.ids.swiper.set_current(self.counter)

    def _stop_animation(self):
        self.clock.cancel()

    def change_theme(self):
        from kivymd.uix.button import MDRaisedButton, MDFlatButton

        def restart_app(*args):
            with open("theme.txt", "w") as theme:
                theme.write("Dark") if self.app.theme_cls.theme_style == "Light" else theme.write("Light")
                self.app.stop()

        def dismiss_dialog(*args):
            dialog.dismiss()

        button1 = MDFlatButton(text="Cancel", on_release=dismiss_dialog)
        button2 = MDRaisedButton(text="Continue", on_release=restart_app)
        dialog = MDDialog(
            title="Change Theme",
            text="app restart is required for Dark Mode" if self.app.theme_cls.theme_style == "Light"
            else "app restart is required for Light Mode",
            buttons=[button1, button2], auto_dismiss=False
        )
        dialog.open()

    def add_nav(self, item):
        if item.children:
            return
        exec(f"from libs.libpy import {item.name}")
        Thread(target=self._thread_build, args=(item,)).start()

    def _thread_build(self, item):
        Builder.load_file(f"libs/libkv/main/{item.name}.kv")
        self._add_nav_item(item)

    @mainthread
    def _add_nav_item(self, item):
        exec("from kivy.factory import Factory")
        item.add_widget(eval(f"Factory.{item.name.capitalize()}()"))

    @staticmethod
    def outline(icon: list, instance):
        if instance and "outline" in instance.icon:
            instance.icon = instance.icon.strip("outline").strip("-")
        for i in icon:
            if "outline" in i.icon:
                continue
            i.icon += "-outline"

    def on_menu(self):
        self.menu.open()
