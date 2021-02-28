from json import dumps, loads
from classes.notification import notify
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen


class ProductLookOut(Screen):
    url = "https://nocenstore.pythonanywhere.com/"
    tmp_data = None

    def go_back(self):
        self.manager.current = "category"

    def update_interface(self, data):
        self.tmp_data = data
        UrlRequest(
            url=f"{self.url}showcaseProduct",
            req_body=dumps(data),
            on_error=self.network_error,
            on_success=self.post_data
        )

    def network_error(self, *args):
        notify("You lost connection, check your Internet settings")
        self.update_interface(self.tmp_data)

    def post_data(self, instance, data):
        new_data = loads(data)
        self.ids.product_price.text = f"₦{new_data['price']}"
        self.ids.description.text = new_data["description"]
        for i in range(1, 4):
            self.ids[f"image{i}"].source = new_data[str(i)]

    def change_circle(self):
        for i in range(1, 4):
            if self.ids.mg.current == str(i):
                self.ids[f"ico{i}"].icon = "circle"
                continue
            self.ids[f"ico{i}"].icon = "circle-outline"

    def clear_cache(self):
        for i in range(1, 4):
            self.ids[f"image{i}"].source = ""
        self.ids.product_price.text = ""
        self.ids.description.text = ""
