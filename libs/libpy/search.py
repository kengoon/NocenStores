from json import loads
from classes.notification import notify
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen
from functions.dict_search import search_engine


class Search(Screen):
    update = True
    data = []
    url = "https://nocenstore.pythonanywhere.com/"
    toast = True
    search_product = False
    blink = True
    wait_search = False

    def go_home(self, *args):
        self.manager.current = "home"

    def on_enter(self, *args):
        self.get_data()

    def get_data(self):
        UrlRequest(
            url=f"{self.url}getTrendingProduct",
            on_error=self.network_error,
            on_success=self.post_data,
            on_failure=self.server_error
        )

    def post_data(self, instance, data):
        print(data)
        self.ids.progress_box.opacity = 0
        if data == "None":
            self.ids.non.opacity = 1
            self.ids.ico.icon = "package-variant-closed"
            self.ids.lbl.text = "No Trending Product"
            return
        self.data = loads(data)
        self.search_product = True
        self.search(None) if self.wait_search else None
        self.wait_search = False

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

    def search(self, instance):
        self.ids.holder.clear_widgets()
        self.ids.rv.data = []
        if self.blink:
            self.ids.progress_box.opacity = 1
            self.blink = False
        if not self.data:
            notify("searching..  ")
            self.wait_search = True
            return
        search_term = self.ids.txt.text.split()
        for index, _ in enumerate(search_term):
            search_term[index] = search_term[index].capitalize()
        search_term = " ".join(search_term)
        product = search_engine(search_term, "product", self.data)
        if not product:
            self.ids.ico.icon = "cloud-off-outline"
            self.ids.lbl.text = "Search Term Not Found"
            self.ids.non.opacity = 1
            self.ids.progress_box.opacity = 0
            notify("search term not found")
            return
        for i in product:
            print(i)
            self.ids.rv.data.append(i)
        print(search_term)
        self.ids.progress_box.opacity = 0
        self.ids.non.opacity = 0
        self.blink = True
