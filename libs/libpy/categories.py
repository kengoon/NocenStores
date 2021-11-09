from json import dumps, loads
from os import mkdir
from os.path import exists
from threading import Thread

from kivy.clock import Clock, mainthread
from kivy.core.window import Window

from classes.notification import notify
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen


class Category(Screen):
    data_type = ""
    update = False
    menu = None
    url = "https://nocenstore.pythonanywhere.com/"
    clock = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        self.tmp_data = []
        self.request = None

    def on_enter(self, *args):
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

    def update_data(self, instance, data):
        if not self.clock:
            self.clock = Clock.schedule_interval(self.get_data, 30)
        if data == "None":
            self.post_data(data=data)
            return
        if not self.data:
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
        self.ids.progress_box.opacity = 0
        if data == "None":
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "No product for this category yet"
            return
        length_data = len(self.data)
        new_data = []
        for index, _ in enumerate(range(length_data)):
            if index == 20:
                break
            _data = self.data.pop(0)
            _data.update({"_size": [0, Window.height/2.5], "source": "assets/loader.gif"})
            new_data.append(_data)
        self.ids.rv.data.extend(new_data)
        if not exists(f"tmp/{self.data_type.replace(' ', '_')}"):
            mkdir(f"tmp/{self.data_type.replace(' ', '_')}")
            for index, data_dic in enumerate(new_data):
                Thread(target=self.get_raw_image, args=(data_dic, index)).start()

    def get_raw_image(self, data_dic, index):
        while True:
            import requests
            from PIL import Image
            try:
                var = self.data_type.replace(" ", "_")
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

    def check_network(self, instance, data):
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
        Clock.schedule_once(self.check_update_data, 2)

    def check_update_data(self, *args):
        exec(f"self.{self.exec_type}_data = self.{self.exec_type}_data")
        if eval(f"self.{self.exec_type}_data"):
            length_data = eval(f"len(self.{self.exec_type}_data)")
            for index, _ in enumerate(range(length_data)):
                if index == 20:
                    break
                self.ids.rv.data.append(eval(f"self.{self.exec_type}_data.pop(0)"))
