import os
import urllib.request
from functools import partial
from json import loads
from os import listdir
from os.path import exists
from threading import Thread
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd_extensions.sweetalert import SweetAlert
from classes.notification import notify


class Home(Screen, EventDispatcher):
    app = MDApp.get_running_app()
    clock = ObjectProperty()
    counter = NumericProperty(0)
    update = False
    pause = False
    menu = None
    url = "https://nocenstore.pythonanywhere.com/"
    toast = True
    data_trending = []
    swiper = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_menu")
        self.alert = SweetAlert(size_hint_x=None, width=Window.width - dp(20))
        self.data = []
        self.widgets = [
            {"viewclass": "LogoPanel", "root": self, "_size": [0, Window.height / 7]},
            {"viewclass": "Swiper", "root": self, "_size": [0, Window.height / 4]},
            # {"viewclass": "EasySearch", "root": self, "_size": [0, dp(150)]},
            # {"viewclass": "Gridad", "root": self, "_size": [0, Window.height]}
        ]

    def go_cart(self):
        self.manager.prev_screen.append(self.name)
        from tools import check_add_widget
        from kivy.factory import Factory
        check_add_widget(self.app, "cart_widget", self, Factory.Cart(), "cart")
        self.manager.current = "cart"

    def fire(self):
        logout = MDRaisedButton(text="LOG OUT", on_release=self.delete_token)
        logout.md_bg_color = get_color_from_hex('#dd3b34')
        self.alert.fire(
            "Your email is not verified. Visit your email provider (gmail, outlook,....) to verify your email",
            buttons=[MDRaisedButton(text="CONTINUE", on_release=self.check_email),
                     logout],
            type="info"
        )

    def delete_token(self, instance):
        self.alert.dismiss()
        self.app.firebase = {}
        os.remove("token.json")
        from tools import check_add_widget
        from kivy.factory import Factory
        check_add_widget(self.app, "login_widget", self, Factory.Login(), "login")
        self.manager.current = "login"

    def on_enter(self, *args):
        if not exists("tmp"):
            os.mkdir("tmp")
        if self.app.firebase and not self.app.firebase["profile"]["users"][0]["emailVerified"]:
            self.fire()
        if self.update:
            return
        Clock.schedule_once(self.screen_update, 7)

    def check_email(self, instance):
        self.alert.content_cls.children[1].text = "Checking if you have verified your email"
        self.alert.request = True

        def check(instance, data):
            if data == "False":
                self.alert.dismiss()
                self.alert = SweetAlert(size_hint_x=None, width=Window.width - dp(20))
                self.fire()
            else:
                self.app.firebase["profile"]["users"][0]["emailVerified"] = True
                self.alert.dismiss()

        UrlRequest(
            self.url + "verifyEmail",
            req_body=str(self.app.firebase["refreshToken"]),
            on_success=check,
            on_failure=lambda x: print("failed")
        )

    def screen_update(self, *args):
        for data in self.widgets:
            self.ids.rv.data.append(data)
        self.get_ads()
        self.get_data()
        self.start_clock()
        self.update = True

    def start_clock(self):
        self.clock = Clock.schedule_interval(self._start_animation, 5)

    def get_ads(self):
        # UrlRequest(
        #     url=f"{self.url}get_ads",
        #     on_success=self.update_ads_data,
        #     on_error=self.check_cache
        # )
        pass

    def update_ads_data(self, instance, data):
        data = loads(data)
        Thread(target=partial(self.download_ads, data)).start()
        # for content, child in zip(data, self.ids.swiper.children[0].children):
        # self.swiper = self.ids.holder.children[-1].ids.swiper
        for content, child in zip(data, self.swiper.children[0].children):
            child.children[0].children[0].source = content["image_url"]
            child.children[0].children[0].text = content["name"]

    @staticmethod
    def download_ads(data):
        for i, image in enumerate(data):
            urllib.request.urlretrieve(image["image_url"], f"assets/ads/{i}.jpg")

    def check_cache(self, *args):
        self.get_ads()
        if listdir("assets/ads"):
            # self.swiper = self.ids.holder.children[-1].ids.swiper
            for image, child in zip(listdir("assets/ads"), self.swiper.children[0].children):
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
        self.counter = self.swiper.get_current_index() + 1
        self.counter = 0 if self.counter == 5 else self.counter
        try:
            self.swiper = self.ids.holder.children[-1].ids.swiper
        except AttributeError:
            pass
        self.swiper.set_current(self.counter)

    def _stop_animation(self):
        self.clock.cancel()

    def change_theme(self):
        with open("theme.txt", "w") as theme:
            theme.write("Dark") if self.app.theme_cls.theme_style == "Light" else theme.write("Light")
            self.app.theme_no_active = True
            self.app.theme_cls.theme_style = "Dark" if self.app.theme_cls.theme_style == "Light" else "Light"

    @staticmethod
    def outline(icon: list, instance):
        pass

    def on_menu(self):
        self.menu.open()

    def open_menu(self, instance):
        self.manager.current = "menu"

    def change_screen(self, instance, screen, dialog):
        self.manager.on_next_screen(self.name)
        from tools import check_add_widget
        from kivy.factory import Factory
        check_add_widget(self.app, f"{screen}_widget", self, Factory.Category(name=screen), screen)
        self.manager.ids[screen].data_type = \
            instance.text.lower() if instance.text.lower() != "portables" else "portable devices"
        # self.manager.ids.category.exec_type = "_".join(
        #     instance.text.lower().split(" ") if instance.text.lower() != "portables" else "portable devices".split(" ")
        # )
        self.manager.current = screen
        dialog.dismiss()

    def get_data(self):
        UrlRequest(
            url=f"{self.url}getTrendingProduct",
            on_error=self.network_error,
            on_success=self.post_data,
            on_failure=self.server_error
        )

    def post_data(self, instance, data):
        if data == "None":
            return
        self.data_trending = loads(data)
        length_data = len(self.data_trending)
        new_data = []
        for index, _ in enumerate(range(length_data)):
            if index == 20:
                break
            datum = self.data_trending.pop(0)

            datum.update(
                {
                    "viewclass": "HomeProductCard",
                    "_size": [0, Window.height/4.5],
                    "texture": Texture.create(size=(1, 1), colorfmt='rgba'),
                    "canvas_texture": None,
                    "rv": self.ids.rv,
                    "source": "assets/loader.gif"
                }
            )
            new_data.append(datum)
        self.ids.rv.data.extend(new_data)
        for index, data_dic in enumerate(new_data):
            Thread(target=self.get_raw_image, args=(data_dic, index)).start()

    def get_raw_image(self, data_dic, index):
        while True:
            import requests
            from PIL import Image
            try:
                response = requests.get(data_dic["imagePath"], stream=True)
                response.raw.decode_content = True
                Image.open(response.raw).convert("RGB").save(f"tmp/{index}.jpg")
                self.update_data_texture(index, f"tmp/{index}.jpg")
                break
            except requests.exceptions.RequestException:
                pass

    @mainthread
    def update_data_texture(self, index, texture):
        self.ids.rv.data[index + 2]["source"] = texture
        self.ids.rv.refresh_from_data()

    def network_error(self, instance, data):
        self.get_data()
        if self.toast:
            notify("please turn on your data or subscribe")
            self.toast = False

    @staticmethod
    def server_error(instance, data):
        notify("server is being updated, will be fixed soon")

    def schedule_load(self):
        def continue_update(*args):
            if self.data_trending:
                length_data = len(self.data_trending)
                for i, _ in enumerate(range(length_data)):
                    if i == 20:
                        break
                    datum = self.data_trending.pop(0)
                    datum.update({"viewclass": "HomeProductCard"})
                    self.ids.rv.data.append(datum)

        Clock.schedule_once(continue_update, 2)
