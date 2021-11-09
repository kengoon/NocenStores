import webbrowser
from json import loads

from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from classes.notification import notify
from kivy.app import App


class Feeds(Screen):
    update = True
    url = "https://nocenstore.pythonanywhere.com/"
    toast = True
    data = []
    root = ObjectProperty()
    app = App.get_running_app()

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

    def schedule_load(self):
        def continue_update(*args):
            if self.data:
                length_data = len(self.data)
                for i, _ in enumerate(range(length_data)):
                    if i == 20:
                        break
                    self.ids.rv.data.insert(0, self.data.pop(0))

        Clock.schedule_once(continue_update, 2)

    def go_cart(self, instance):
        self.root.manager.prev_screen.append(self.root.name)
        from tools import check_add_widget
        from kivy.factory import Factory
        check_add_widget(self.app, "cart_widget", self.root, Factory.Cart(), "cart")
        self.root.manager.current = "cart"

    def proceed_to_lookout(self, instance):
        if instance.url:
            webbrowser.open(instance.url)
            return
        if not instance.price:
            return
        self.root.manager.prev_screen.append(self.root.name)
        from tools import check_add_widget
        from kivy.factory import Factory
        check_add_widget(self.app, "lookout_widget", self.root, Factory.ProductLookOut(), "lookout")
        self.root.manager.current = "lookout"
        self.root.manager.ids.lookout.ids.product_name.text = instance.name
        self.root.manager.ids.lookout.ids.store.text = instance.store
        self.root.manager.ids.lookout.update_interface(instance.data)
