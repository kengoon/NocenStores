from json import loads, dumps
from os import mkdir
from os.path import exists
from threading import Thread

from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.utils import get_color_from_hex
from kivymd.uix.button import MDFlatButton
from kivymd.uix.snackbar import Snackbar

from classes.notification import notify
from kivy.app import App


class Used(Screen):
    root = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update = True
        self.url = "https://nocenstore.pythonanywhere.com/"
        self.toast = True
        self.data = []
        self.app = App.get_running_app()
        self.image_loaded = 0
        self.len_rv_data = 0
        self.snack = Snackbar(
            text="LOAD MORE PRODUCTS??!!",
            bg_color=get_color_from_hex("#2962FF"),
            snackbar_x="20dp", snackbar_y="20dp",
            size_hint_x=(Window.width - dp(40)) / Window.width,
            radius=[dp(10)],
            buttons=[MDFlatButton(
                text="YES", theme_text_color="Custom",
                text_color=self.app.theme_cls.accent_color,
                on_release=self.schedule_load
            )]
        )
        self.snack.auto_dismiss = False

    def on_enter(self):
        if not exists("tmp/used"):
            mkdir("tmp/used")
        if self.update:
            self.get_data()
            self.update = False

    def get_data(self):
        UrlRequest(
            url=f"{self.url}getFairlyUsedProduct",
            on_error=self.network_error,
            on_success=self.post_data,
            on_failure=self.server_error
        )

    def post_data(self, instance, data):
        if data == "None":
            self.ids.progress_box.opacity = 0
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "Fairly Used Products Unavailable"
            return
        self.data = loads(data)
        length_data = len(self.data)
        self.modify_product_data(length_data, transmit=True)

    def get_raw_image(self, data_dic, index):
        while True:
            import requests
            from PIL import Image
            try:
                var = "used"
                response = requests.get(data_dic["imagePath"], stream=True)
                response.raw.decode_content = True
                Image.open(response.raw).convert("RGB").save(f"tmp/{var}/{index}.jpg")
                self.update_data_texture(index, f"tmp/{var}/{index}.jpg")
                break
            except requests.exceptions.RequestException:
                pass

    @mainthread
    def update_data_texture(self, data_dic):
        self.ids.progress_box.opacity = 0
        self.ids.rv.data.append(data_dic)
        self.image_loaded += 1

    def network_error(self, instance, data):
        self.ids.progress_box.opacity = 0
        self.ids.non.opacity = 1
        self.ids.ico.icon = "network-strength-off-outline"
        self.ids.lbl.text = "please turn on your data\nor subscribe"
        notify("please turn on your data or subscribe")

    def server_error(self, instance, data):
        self.ids.progress_box.opacity = 0
        self.ids.non.opacity = 1
        self.ids.ico.icon = "server-network-off"
        self.ids.lbl.text = "server is being updated, will be fixed soon"
        notify("server is being updated, will be fixed soon")

    def schedule_load(self, *_):
        self.snack.dismiss()
        if self.data and (self.image_loaded == self.len_rv_data):
            length_data = len(self.data)
            self.modify_product_data(length_data, transmit=True)

    def go_cart(self):
        self.root.manager.prev_screen.append(self.root.name)
        from tools import check_add_widget
        check_add_widget(self.app, "cart_widget", self.root, "Factory.Cart()", "cart")
        self.root.manager.current = "cart"

    def modify_product_data(self, length_data, transmit=False):
        new_data = []
        for index, _ in enumerate(range(length_data)):
            if index == 20:
                break
            datum = self.data.pop(0)
            datum.update(
                {
                    "_size": [self.width/2 - dp(20), Window.height/2.5],
                    "source": "assets/loader.gif"
                }
            )
            new_data.append(datum)
            self.len_rv_data += 1
        for index, data_dic in enumerate(new_data):
            if transmit:
                bytes_data = dumps([data_dic, index + len(self.ids.rv.data), self.name]).encode("utf8")
                self.app.client.send_message(b"/receive_data", [bytes_data])
                continue
            Thread(target=self.get_raw_image, args=(data_dic, index + len(self.ids.rv.data))).start()

