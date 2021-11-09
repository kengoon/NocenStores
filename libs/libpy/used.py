from json import loads
from os import mkdir
from os.path import exists
from threading import Thread

from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from classes.notification import notify
from kivy.app import App


class Used(Screen):
    update = True
    url = "https://nocenstore.pythonanywhere.com/"
    toast = True
    data = []
    root = ObjectProperty()
    app = App.get_running_app()

    def on_enter(self):
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
        self.ids.progress_box.opacity = 0
        if data == "None":
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "Fairly Used Products Unavailable"
            return
        self.data = loads(data)
        length_data = len(self.data)
        new_data = []
        for index, _ in enumerate(range(length_data)):
            if index == 20:
                break
            _data = self.data.pop(0)
            _data.update({"_size": [self.width/2 - dp(20), Window.height/2.5], "source": "assets/loader.gif"})
            new_data.append(_data)
        self.ids.rv.data.extend(new_data)
        if not exists("tmp/used"):
            mkdir("tmp/used")
            for index, data_dic in enumerate(new_data):
                Thread(target=self.get_raw_image, args=(data_dic, index)).start()

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
    def update_data_texture(self, index, texture):
        self.ids.rv.data[index]["source"] = texture
        self.ids.rv.refresh_from_data()

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

    def schedule_load(self):
        def continue_update(*args):
            if self.data:
                length_data = len(self.data)
                for i, _ in enumerate(range(length_data)):
                    if i == 20:
                        break
                    self.ids.rv.data.append(self.data.pop(0))

        Clock.schedule_once(continue_update, 5)

    def go_cart(self, instance):
        self.root.manager.prev_screen.append(self.root.name)
        from tools import check_add_widget
        from kivy.factory import Factory
        check_add_widget(self.app, "cart_widget", self.root, Factory.Cart(), "cart")
        self.root.manager.current = "cart"
