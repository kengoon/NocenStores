from json import loads

from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen
from classes.notification import notify


class Feeds(Screen):
    update = True
    url = "https://nocenstore.pythonanywhere.com/"
    toast = True
    data = []

    def on_enter(self):
        if self.update:
            self.get_data()

    def get_data(self):
        UrlRequest(
            url=f"{self.url}get_ads",
            on_error=self.network_error,
            on_success=self.post_data,
            on_failure=self.server_error
        )

    def post_data(self, instance, data):
        self.ids.progress_box.opacity = 0
        if data == "None":
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "No Feeds"
            return
        self.data = loads(data)
        length_data = len(self.data)
        for index, _ in enumerate(range(length_data)):
            if index == 20:
                break
            self.ids.rv.data.append(self.data.pop(0))
        self.update = False

    def network_error(self, instance, data):
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

    def schedule_load(self):
        def continue_update(*args):
            if self.data:
                length_data = len(self.data)
                for i, _ in enumerate(range(length_data)):
                    if i == 20:
                        break
                    self.ids.rv.data.append(self.data.pop(0))

        Clock.schedule_once(continue_update, 5)
