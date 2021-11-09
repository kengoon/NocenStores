from json import loads

from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen
from kivy.app import App
from classes.notification import notify


class Deals(Screen):
    update = True
    url = "https://nocenstore.pythonanywhere.com/"
    toast = True
    data = []
    app = App.get_running_app()

    def on_enter(self):
        if self.update:
            self.get_data()

    def enter_search(self):
        from tools import check_add_widget
        from kivy.factory import Factory
        check_add_widget(self.app, "search_widget", self, Factory.Search(), "search")
        self.manager.ids.search.p_type = True
        self.manager.current = "search"

    def get_data(self):
        UrlRequest(
            url=f"{self.url}getAllDeals",
            on_error=self.network_error,
            on_success=self.post_data,
            on_failure=self.server_error
        )

    def post_data(self, instance, data):
        self.ids.progress_box.opacity = 0
        if data == "None":
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "No Deals Today"
            return
        self.data = loads(data)
        length_data = len(self.data)
        for index, _ in enumerate(range(length_data)):
            if index == 20:
                break
            self.ids.rv.data.insert(0, self.data.pop(0))
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

    def go_home(self):
        self.manager.current = "home"

    def schedule_load(self):
        def continue_update(*args):
            if self.data:
                length_data = len(self.data)
                for i, _ in enumerate(range(length_data)):
                    if i == 20:
                        break
                    self.ids.rv.data.insert(0, self.data.pop(0))
        Clock.schedule_once(continue_update, 2)
