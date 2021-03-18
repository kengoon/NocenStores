from json import loads

from kivy.uix.screenmanager import Screen
from kivy import platform
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest

if platform == "android":
    import android_webview


class StudentInfo(Screen):
    update = True
    data = []
    tmp_data = []
    url = "https://nocenstore.pythonanywhere.com/"

    def go_home(self):
        self.manager.current = "home"

    @staticmethod
    def open_web(self):
        if platform == "android" and self.news_url:
            android_webview.webbrowser.open(self.news_url)

    def on_enter(self, *args):
        if self.update:
            self.get_data()
            Clock.schedule_interval(self.get_data, 5)
            self.update = False

    def get_data(self, *args):
        UrlRequest(
            self.url + "GetNews",
            on_error=self.network_error,
            on_failure=self.server_error,
            on_success=self.update_data,
        )

    def update_data(self, instance, data):
        if data == "None":
            self.post_data(data=data)
            return
        if not self.tmp_data:
            self.tmp_data = loads(data)
            self.data = self.tmp_data.copy()
        elif len(loads(data)) > len(self.tmp_data):
            data_len = len(loads(data)) - len(self.tmp_data)
            self.tmp_data = loads(data)
            for i in range(data_len):
                self.data.append(self.tmp_data[i - data_len])
        else:
            return
        print(self.data)
        self.post_data()

    def post_data(self, data="not_empty"):
        self.ids.progress_box.opacity = 0
        if data == "None":
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "No product for this category yet"
            return
        length_data = len(self.data)
        for index, _ in enumerate(range(length_data)):
            if index == 20:
                break
            self.ids.rv.data.insert(0, self.data.pop(0))

    def network_error(self, instance, data):
        self.get_data()
        self.ids.progress_box.opacity = 0
        self.ids.non.opacity = 1
        self.ids.ico.icon = "network-strength-off-outline"
        self.ids.lbl.text = "please turn on your data\nor subscribe"

    def server_error(self, instance, data):
        self.ids.progress_box.opacity = 0
        self.ids.non.opacity = 1
        self.ids.ico.icon = "server-network-off"
        self.ids.lbl.text = "server is being updated, will be fixed soon"

    def schedule_load(self):
        def continue_update(*args):
            if self.data:
                length_data = len(self.data)
                for i, _ in enumerate(range(length_data)):
                    if i == 20:
                        break
                    self.ids.rv.data.append(self.data.pop(0))

        Clock.schedule_once(continue_update, 2)

