from json import dumps, loads
from os import mkdir
from os.path import exists
from threading import Thread
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivymd.uix.button import MDFlatButton
from kivymd.uix.snackbar import Snackbar

from classes.notification import notify
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen


class Category(Screen):
    data_type = ""
    update = False
    menu = None
    url = "https://nocenstore.pythonanywhere.com/"
    clock = None
    app = App.get_running_app()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        self.tmp_data = []
        self.request = None
        self.image_loaded = 0
        self.len_rv_data = 0
        self.set_error_message = True
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

    def on_enter(self, *args):
        if not exists(f"tmp/{self.name.replace(' ', '_')}"):
            mkdir(f"tmp/{self.name.replace(' ', '_')}")
        if not self.update:
            self.request = self.get_data()

    def go_home(self, *args):
        self.manager.current = "home"

    def get_data(self, *args):
        return UrlRequest(
            url=self.url + "getCategoryType",
            req_body=dumps({"type": self.data_type}),
            on_success=self.update_data,
            on_error=self.check_network,
            on_failure=self.server_error
        )

    def update_data(self, instance, data): # NOQA
        if not self.clock:
            self.clock = Clock.schedule_interval(self.get_data, 30)
        if data == "None":
            self.post_data(data=data)
            return
        if not self.data and not self.tmp_data:
            self.tmp_data = loads(data)
            self.data = self.tmp_data.copy()
        elif len(loads(data)) > len(self.tmp_data):
            counter = len(loads(data)) - len(self.tmp_data)
            self.tmp_data = loads(data)
            for _ in range(counter):
                self.data.append(self.tmp_data[(_ + 1) - counter])
        else:
            return

        self.post_data()
        self.update = True

    def post_data(self, data=""):
        self.set_error_message = False
        if data == "None":
            self.ids.progress_box.opacity = 0
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "No product for this category yet"
            return
        self.ids.non.opacity = 0
        length_data = len(self.data)
        self.modify_product_data(length_data, transmit=True)

    def get_raw_image(self, data_dic, index):
        while True:
            import requests
            from PIL import Image
            try:
                response = requests.get(data_dic["imagePath"], stream=True)
                response.raw.decode_content = True
                Image.open(response.raw).convert("RGB").save(f"tmp/{index}.jpg")
                data_dic["source"] = f"tmp/{self.name}/{index}.jpg"
                self.update_data_texture(data_dic)
                break
            except requests.exceptions.RequestException:
                pass

    @mainthread
    def update_data_texture(self, data_dic):
        self.ids.progress_box.opacity = 0
        self.ids.rv.data.append(data_dic)
        self.image_loaded += 1

    def check_network(self, *_):
        if self.set_error_message:
            self.ids.progress_box.opacity = 0
            self.ids.non.opacity = 1
            self.ids.ico.icon = "network-strength-off-outline"
            self.ids.lbl.text = "please turn on your data\nor subscribe"
            notify("please turn on your data or subscribe")

    def server_error(self, *args): # NOQA
        if self.set_error_message:
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

    def modify_product_data(self, length_data, transmit=False):
        new_data = []
        for index, _ in enumerate(range(length_data)):
            if index == 20:
                break
            datum = self.data.pop(0)
            datum.update(
                {
                    "_size": [self.width/2 - dp(20), Window.height / 2.5],
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
