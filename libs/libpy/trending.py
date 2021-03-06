from json import loads
from classes.notification import notify
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen


class Trending(Screen):
    data = []
    update = True
    url = "https://nocenstore.pythonanywhere.com/"
    toast = True

    def go_home(self, *args):
        self.manager.current = "home"

    def on_enter(self):
        if self.update:
            self.get_data()

    def get_data(self):
        UrlRequest(
            url=f"{self.url}getTrendingProduct",
            on_error=self.network_error,
            on_success=self.post_data,
            on_failure=self.server_error
        )

    def post_data(self, instance, data):
        self.ids.progress_box.opacity = 0
        if data == "None":
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "No Trending Product"
            return
        self.data = loads(data)
        for _, deals in enumerate(self.data):
            if _ == 20:
                break
            self.ids.rv.data.append(deals)
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
