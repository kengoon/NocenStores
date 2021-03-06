from json import dumps, loads
from kivy.clock import Clock
from classes.notification import notify
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen


class Category(Screen):
    data_type = ""
    exec_type = ""
    update = False
    menu = None
    url = "https://nocenstore.pythonanywhere.com/"
    toast = True
    clock = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stop = False
        self.clothing_data = []
        self.clothing_tmp_data = []
        self.furniture_data = []
        self.furniture_tmp_data = []
        self.kitchen_data = []
        self.kitchen_tmp_data = []
        self.electronics_data = []
        self.electronics_tmp_data = []
        self.beauty_data = []
        self.beauty_tmp_data = []
        self.portable_devices_data = []
        self.portable_devices_tmp_data = []

    def on_pre_enter(self, *args):
        if self.clock:
            self.clock.cancel()
        self.ids.non.opacity = 0
        self.ids.progress_box.opacity = 1

    def on_enter(self, *args):
        self.stop = False
        self.toast = True
        if eval(f"self.{self.exec_type}_tmp_data"):
            exec(f"self.{self.exec_type}_data = self.{self.exec_type}_tmp_data")
            self.post_data()
            self.update = True
        else:
            self.get_data()
        self.clock = Clock.schedule_interval(self.get_data, 30)

    def on_leave(self, *args):
        self.ids.holder.clear_widgets()
        self.ids.rv.data = []
        self.update = False
        # self.clock.cancel()

    def go_home(self, *args):
        self.manager.current = "home"

    def get_data(self, *args):
        UrlRequest(
            url=self.url + "getCategoryType",
            req_body=dumps({"type": self.data_type}),
            on_success=self.update_data,
            on_error=self.check_network,
            on_failure=self.server_error
        )

    def update_data(self, instance, data):
        if data == "None":
            self.post_data(data=data)
            return
        if not eval(f"self.{self.exec_type}_tmp_data"):
            exec(f"self.{self.exec_type}_tmp_data = loads(data)")
            exec(f"self.{self.exec_type}_data = self.{self.exec_type}_tmp_data.copy()")
        # checks if data from net is greater than tmp data and then gets the newest data and adds it to self.data
        elif len(loads(data)) > eval(f"len(self.{self.exec_type}_tmp_data)"):
            counter = len(loads(data)) - eval(f"len(self.{self.exec_type}_tmp_data)")
            exec(f"self.{self.exec_type}_tmp_data = loads(data)")
            for _ in range(counter):
                exec(f"self.{self.exec_type}_data.append(self.{self.exec_type}_tmp_data[_ - counter])")
            self.stop = False

        if not self.update:
            self.post_data()
            self.update = True

    def post_data(self, data="not_empty"):
        self.toast = True
        self.ids.progress_box.opacity = 0
        if data == "None":
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "No product for this category yet"
            return
        length_data = eval(f"len(self.{self.exec_type}_data)")
        for index, _ in enumerate(range(length_data)):
            if index == 20:
                break
            self.ids.rv.data.append(eval(f"self.{self.exec_type}_data.pop(0)"))
        if not eval(f"self.{self.exec_type}_data"):
            self.stop = True

    def check_network(self, instance, data):
        self.get_data()
        if self.toast:
            self.ids.progress_box.opacity = 0
            self.ids.non.opacity = 1
            self.ids.ico.icon = "network-strength-off-outline"
            self.ids.lbl.text = "please turn on your data\nor subscribe"
            notify("please turn on your data or subscribe")
            self.toast = False

    def server_error(self, instance, data):
        self.ids.progress_box.opacity = 0
        self.ids.non.opacity = 1
        self.ids.ico.icon = "server-network-off"
        self.ids.lbl.text = "server is being updated, will be fixed soon"
        notify("server is being updated, will be fixed soon")

    def check_update_data(self):
        if self.stop:
            return
        exec(f"self.{self.exec_type}_data = self.{self.exec_type}_data")
        if eval(f"self.{self.exec_type}_data"):
            length_data = eval(f"len(self.{self.exec_type}_data)")
            for index, _ in enumerate(range(length_data)):
                if index == 20:
                    break
                self.ids.rv.data.append(eval(f"self.{self.exec_type}_data.pop(0)"))
            # avoid adding a particular widget twice
            if not eval(f"self.{self.exec_type}_data"):
                self.stop = True
