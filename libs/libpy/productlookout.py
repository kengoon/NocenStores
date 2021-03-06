from json import dumps, loads
from classes.notification import notify
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen


class ProductLookOut(Screen):
    url = "https://nocenstore.pythonanywhere.com/"
    tmp_data = None
    selected_size = ""

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

        if "size" in new_data["description"]:
            size_list = new_data["description"].split("(")[1].split(")")[0]

            for i in loads(size_list):
                self.ids.rvs.data.append({"text_item": str(i)})

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
        self.ids.rvs.data = []
        self.ids.holder.clear_widgets()

    def save_unsave(self, instance):
        instance.icon = "heart" if "outline" in instance.icon else "heart-outline"

        def process(instance, data):
            notify(data)
            self.manager.ids.saved.ids.rv.data.append(
                {
                    "imagePath": self.ids.image1.source,
                    "price": self.ids.product_price,
                    "product": self.ids.product_name,
                    "store": self.ids
                }
            )

        def network_error(*args):
            notify("network error, please subscribe")
            instance.icon = "heart" if "outline" in instance.icon else "heart-outline"

        def server_error(*args):
            notify("server is down, fixing...")
            instance.icon = "heart" if "outline" in instance.icon else "heart-outline"

        UrlRequest(
            url=self.url + "saveMyProduct",
            on_success=process,
            on_error=network_error,
            on_failure=server_error
        )

    def call(self, instance):
        print(instance)
        self.ids.loader.opacity = 0
