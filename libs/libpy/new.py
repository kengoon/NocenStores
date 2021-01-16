from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu


class New(Screen):
    update = False
    menu = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = [
            {"source": "assets/clock-4.png", "product_price": 1000, "product_name": "crab", "store": "Shoprite",
             "root": self}, {
                "source": "https://image.shutterstock.com/image-photo/view-lagos-lagoon-victoria-island-260nw"
                          "-1066980758.jpg",
                "store": "RobanStores", "product_price": 3000, "product_name": "Checkers"},
            {"source": "assets/clock-4.png", "store": "RobanStores", "product_price": 4000,
             "product_name": "ShowRoom"},
            {"source": "assets/clock-4.png", "store": "RobanStores", "product_price": 4000,
             "product_name": "ShowRoom"},
            {"source": "assets/3.jpg", "store": "Stores", "product_price": 3000, "product_name": "Checkers"},
            {"source": "assets/4.jpg", "product_name": "tent", "product_price": 2300, "store": "Real Estate"},
            {"source": "assets/5.jpg", "store": "RobanStores", "product_price": 3000, "product_name": "Cars"},
            {"source": "assets/5.jpg", "store": "RobanStores", "product_price": 3000, "product_name": "Cars"},
            {"source": "assets/5.jpg", "store": "RobanStores", "product_price": 3000, "product_name": "Cars"}]

    def on_enter(self, *args):
        if not self.update:
            # self.menu = MDDropdownMenu(
            #     caller=self.ids.menu,
            #     items=[
            #         {"icon": "account", "text": "profile"},
            #         {"icon": "cog", "text": "settings"},
            #     ],
            #     width_mult=4,
            #     position="auto"
            # )
            for data in self.data:
                self.ids.rv.data.append(data)
            self.update = True

    pass
