import urllib.request
from functools import partial
from json import loads
from os import listdir
from threading import Thread
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog


class Home(Screen, EventDispatcher):
    app = MDApp.get_running_app()
    clock = ObjectProperty()
    counter = NumericProperty(0)
    update = False
    pause = False
    menu = None
    url = "https://nocenstore.pythonanywhere.com/"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_menu")
        self.data = []

    def go_cart(self, instance):
        self.manager.prev_screen.append(self.name)
        self.manager.current = "cart"

    def on_enter(self, *args):
        if self.update:
            return
        self.start_clock()
        self.get_ads()
        self.ids.home.header.ids._label.font_style = "Caption"
        self.ids.profile.header.ids._label.font_style = "Caption"
        self.ids.sell.header.children[0].remove_widget(self.ids.sell.header.ids._label)
        self.ids.sell.header.ids._label_icon.pos_hint = {"center_x": .5, "center_y": .5}
        self.ids.sell.header.ids._label_icon.font_size = dp(35)
        self.ids.used.header.ids._label.font_style = "Caption"
        self.ids.feeds.header.ids._label.font_style = "Caption"
        for data in self.data:
            self.ids.rc.data.append(data)
        anim = Animation(opacity=0) + Animation(opacity=1)
        anim.repeat = True
        anim.start(self.ids.but)
        self.update = True

    def start_clock(self):
        self.clock = Clock.schedule_interval(self._start_animation, 5)

    def get_ads(self):
        UrlRequest(
            url=f"{self.url}get_ads",
            on_success=self.update_ads_data,
            on_error=self.check_cache
        )

    def update_ads_data(self, instance, data):
        data = loads(data)
        Thread(target=partial(self.download_ads, data)).start()
        for content, child in zip(data, self.ids.swiper.children[0].children):
            child.children[0].children[0].source = content["image_url"]
            child.children[0].children[0].text = content["name"]

    @staticmethod
    def download_ads(data):
        for i, image in enumerate(data):
            urllib.request.urlretrieve(image["image_url"], f"assets/ads/{i}.jpg")

    def check_cache(self, *args):
        self.get_ads()
        if listdir("assets/ads"):
            for image, child in zip(listdir("assets/ads"), self.ids.swiper.children[0].children):
                if child.children[0].children[0].source:
                    return
                child.children[0].children[0].source = f"assets/ads/{image}"

    def pause_clock(self, *args):
        self._stop_animation()
        self.pause = True

    def resume_clock(self):
        if self.pause:
            self.pause = False
            self.start_clock()

    def _start_animation(self, *args):
        self.counter += 1
        self.counter = 0 if self.counter == 5 else self.counter
        self.ids.swiper.set_current(self.counter)

    def _stop_animation(self):
        self.clock.cancel()

    def change_theme(self):
        with open("theme.txt", "w") as theme:
            theme.write("Dark") if self.app.theme_cls.theme_style == "Light" else theme.write("Light")
            self.app.theme_no_active = True
            self.app.theme_cls.theme_style = "Dark" if self.app.theme_cls.theme_style == "Light" else "Light"

        # def dismiss_dialog(*args):
        #     dialog.dismiss()
        #
        # button1 = MDFlatButton(text="Cancel", on_release=dismiss_dialog)
        # button2 = MDRaisedButton(text="Continue", on_release=restart_app)
        # dialog = MDDialog(
        #     title="Change Theme",
        #     text="app restart is required for Dark Mode" if self.app.theme_cls.theme_style == "Light"
        #     else "app restart is required for Light Mode",
        #     buttons=[button1, button2], auto_dismiss=False,
        #     size_hint_x=None,
        #     width=Window.width - dp(20)
        # )
        # dialog.open()

    @staticmethod
    def outline(icon: list, instance):
        if instance and "outline" in instance.icon:
            instance.icon = instance.icon.rstrip("outline").rstrip("-")
        for i in icon:
            if "outline" in i.icon:
                continue
            i.icon += "-outline"

    def on_menu(self):
        self.menu.open()

    def open_menu(self, instance):
        self.manager.current = "menu"

    def change_screen(self, instance, screen):
        self.manager.on_next_screen(self.name)
        self.manager.current = screen
        self.manager.ids.category.data_type = instance.text.lower()
        self.manager.ids.category.exec_type = "_".join(instance.text.lower().split(" "))
