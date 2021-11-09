from json import loads, dumps

from kivy.clock import Clock

from classes.notification import notify
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class SavedProduct(Screen):
    update = True
    url = "https://nocenstore.pythonanywhere.com/"
    toast = True
    data = []
    enter = False
    app = MDApp.get_running_app()

    def enter_search(self):
        self.manager.prev_screen.append(self.name)
        from tools import check_add_widget
        from kivy.factory import Factory
        check_add_widget(self.app, "search_widget", self, Factory.Search(), "search")
        self.manager.ids.search.p_type = True
        self.manager.current = "search"

    def on_enter(self):
        if self.update and self.app.login:
            self.ids.progress_box.opacity = 1
            self.ids.non.opacity = 0
            self.get_data()
        elif not self.app.login:
            self.ids.progress_box.opacity = 0
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "Please Login To View Your Saved Product"

    def get_data(self):
        UrlRequest(
            url=f"{self.url}getMySavedProducts",
            req_body=dumps({"userId": self.app.firebase["userId"]}),
            on_error=self.network_error,
            on_success=self.post_data,
            on_failure=self.server_error
        )

    def post_data(self, instance, data):
        self.ids.progress_box.opacity = 0
        if data == "None":
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "You have not saved any product yet"
            return
        self.data = loads(data)
        length_data = len(self.data)
        for index, _ in enumerate(range(length_data)):
            if index == 20:
                break
            self.ids.rv.data.append(self.data.pop(0))
        self.update = False
        self.enter = True

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
                    self.ids.rv.data.append(self.data.pop(0))
        Clock.schedule_once(continue_update, 5)
